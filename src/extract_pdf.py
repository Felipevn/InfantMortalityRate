import unicodedata
import pandas as pd
import pdfplumber
from .paths import DATA_RAW, DATA_PROC

def norm(s: str) -> str:
    s = "" if s is None else str(s)
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).upper().strip()

def build_mapping(pdf_name: str = "Lista_Municípios_Macrorregião_Porte_Associacoes_1.pdf") -> None:
    rows = []
    pdf_path = DATA_RAW / pdf_name
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for tb in tables:
                header_i = None
                for i, r in enumerate(tb):
                    header_text = norm(" ".join((c or "") for c in r))
                    if "MUNICIPIO" in header_text and "ASSOCIACAO" in header_text:
                        header_i = i; break
                start = (header_i + 1) if header_i is not None else 0
                idx_mun, idx_assoc = 1, -1
                buffer_mun = None
                for r in tb[start:]:
                    cells = [(c or "").replace("\n"," ").strip() for c in r]
                    if not cells: continue
                    mun_raw = cells[idx_mun] if len(cells) > idx_mun else ""
                    assoc_raw = cells[idx_assoc] if len(cells) else ""
                    m, a = norm(mun_raw), norm(assoc_raw)
                    if m and a:
                        rows.append((mun_raw, a)); buffer_mun=None
                    elif m and not a:
                        buffer_mun = mun_raw
                    elif not m and a and buffer_mun:
                        rows.append((buffer_mun, a)); buffer_mun=None
    mapa = pd.DataFrame(rows, columns=["municipio","assoc_raw"]).drop_duplicates()
    mapa["municipio_norm"] = mapa["municipio"].map(norm)
    mapa["assoc"] = mapa["assoc_raw"].map(norm)
    out = DATA_PROC / "municipio_para_assoc.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    mapa[["municipio_norm","assoc"]].to_csv(out, index=False)
    print(f"✅ mapping salvo em: {out}")

if __name__ == "__main__":
    build_mapping()
