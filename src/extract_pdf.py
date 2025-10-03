import unicodedata, pandas as pd, pdfplumber
from .paths import DATA_RAW, DATA_PROC
def norm(s): s="" if s is None else str(s); return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).upper().strip()
def build_mapping(pdf_name="Lista_Municípios_Macrorregião_Porte_Associacoes_1.pdf"):
    rows=[]; pdf_path=DATA_RAW/pdf_name
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            for tb in (p.extract_tables() or []):
                header_i=None
                for i,r in enumerate(tb):
                    t=norm(" ".join((c or "") for c in r))
                    if "MUNICIPIO" in t and "ASSOCIACAO" in t: header_i=i; break
                start=(header_i+1) if header_i is not None else 0
                idx_mun, idx_assoc = 1, -1; buffer=None
                for r in tb[start:]:
                    cells=[(c or "").replace("\n"," ").strip() for c in r]
                    if not cells: continue
                    mun=cells[idx_mun] if len(cells)>idx_mun else ""; assoc=cells[idx_assoc] if cells else ""
                    m,a=norm(mun),norm(assoc)
                    if m and a: rows.append((mun,a)); buffer=None
                    elif m and not a: buffer=mun
                    elif not m and a and buffer: rows.append((buffer,a)); buffer=None
    df=pd.DataFrame(rows,columns=["municipio","assoc_raw"]).drop_duplicates()
    df["municipio_norm"]=df["municipio"].map(norm); df["assoc"]=df["assoc_raw"].map(norm)
    out=DATA_PROC/"municipio_para_assoc.csv"; out.parent.mkdir(parents=True,exist_ok=True)
    df[["municipio_norm","assoc"]].to_csv(out,index=False)
    print(f"✅ mapping salvo em: {out}")
if __name__=="__main__": build_mapping()
