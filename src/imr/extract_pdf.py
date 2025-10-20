import unicodedata, pandas as pd, pdfplumber
from .paths import DATA_RAW, DATA_PROC

# -------------------------------------------------------------
# Function: norm()
# Purpose:  Normalize text by removing accents, uppercasing,
#           and stripping whitespace.
# -------------------------------------------------------------
def norm(s):
    # Convert None to empty string and ensure input is string
    s = "" if s is None else str(s)
    # Normalize Unicode characters (e.g., "é" → "e") and remove diacritics
    s = "".join(
        ch for ch in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(ch)
    )
    # Return uppercase, trimmed string
    return s.upper().strip()


# -------------------------------------------------------------
# Function: build_mapping()
# Purpose:  Extract mapping between municipalities and
#           associations from a structured PDF table.
# Input:    pdf_name – filename of the PDF inside DATA_RAW folder
# Output:   CSV file: municipio_norm ↔ assoc
# -------------------------------------------------------------
def build_mapping(pdf_name="Lista_Municípios_Macrorregião_Porte_Associacoes_1.pdf"):
    rows = []  # list to hold extracted (municipio, assoc) pairs
    pdf_path = DATA_RAW / pdf_name

    # Open the PDF file using pdfplumber (auto-closes on exit)
    with pdfplumber.open(pdf_path) as pdf:
        # Iterate through all pages of the PDF
        for p in pdf.pages:
            # Extract all tables from the page (may return None)
            for tb in (p.extract_tables() or []):
                header_i = None  # index of the header row

                # --- Step 1: find the header row that contains "MUNICIPIO" and "ASSOCIACAO"
                for i, r in enumerate(tb):
                    # Join all cell texts into one string and normalize
                    t = norm(" ".join((c or "") for c in r))
                    if "MUNICIPIO" in t and "ASSOCIACAO" in t:
                        header_i = i
                        break

                # If header found, start reading data after it; otherwise, start from 0
                start = (header_i + 1) if header_i is not None else 0

                # Default column positions: assume 2nd column is "municipio" and last is "assoc"
                idx_mun, idx_assoc = 1, -1
                buffer = None  # used to temporarily hold municipality names split across rows

                # --- Step 2: iterate over the table rows after the header
                for r in tb[start:]:
                    # Clean line breaks and whitespace
                    cells = [(c or "").replace("\n", " ").strip() for c in r]
                    if not cells:
                        continue  # skip empty rows

                    # Safely get cell values (avoid index errors)
                    mun = cells[idx_mun] if len(cells) > idx_mun else ""
                    assoc = cells[idx_assoc] if cells else ""

                    # Normalize both strings
                    m, a = norm(mun), norm(assoc)

                    # --- Step 3: identify cases
                    if m and a:
                        # Case A: both municipality and association on same line
                        rows.append((mun, a))
                        buffer = None
                    elif m and not a:
                        # Case B: municipality present but association missing (likely continues next line)
                        buffer = mun
                    elif not m and a and buffer:
                        # Case C: association appears on next line, use previous buffered municipality
                        rows.append((buffer, a))
                        buffer = None

    # --- Step 4: build final DataFrame and clean duplicates
    df = pd.DataFrame(rows, columns=["municipio", "assoc_raw"]).drop_duplicates()

    # Add normalized columns for easier joins and comparisons
    df["municipio_norm"] = df["municipio"].map(norm)
    df["assoc"] = df["assoc_raw"].map(norm)

    # --- Step 5: save mapping to CSV file
    out = DATA_PROC / "municipio_para_assoc.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df[["municipio_norm", "assoc"]].to_csv(out, index=False)

    print(f"✅ Mapping saved at: {out}")


# -------------------------------------------------------------
# Main script entry point (runs when executed directly)
# -------------------------------------------------------------
if __name__ == "__main__":
    build_mapping()
