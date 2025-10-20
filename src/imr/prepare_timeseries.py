import unicodedata, pandas as pd
from .paths import DATA_RAW, DATA_PROC

# -------------------------------------------------------------
# Text normalization helper:
# - Convert None -> ""
# - Unicode NFKD decomposition (e.g., "ç" -> "c")
# - Remove diacritics
# - Uppercase and trim
# Useful to make joins and comparisons accent/case-insensitive.
# -------------------------------------------------------------
def norm(s):
    s = "" if s is None else str(s)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(ch)
    ).upper().strip()


def run(xlsx="mortalidade.xlsx"):
    """
    Load the raw Excel file, standardize column names/types,
    normalize the association label, and export a clean CSV (dfm.csv).

    Input (under DATA_RAW):
      - xlsx: Excel file with columns 'Região', 'Ano', 'Mortalidade'

    Output (under DATA_PROC):
      - dfm.csv with columns: ['assoc', 'ano', 'tmi']
    """

    # 1) Read Excel and rename source columns to the canonical schema
    df = (
        pd.read_excel(DATA_RAW / xlsx)
          .rename(columns={"Região": "assoc", "Ano": "ano", "Mortalidade": "tmi"})
    )

    # 2) Normalize association names (remove accents, uppercase) for reliable joins
    df["assoc"] = df["assoc"].map(norm)

    # 3) Coerce numeric columns; 'ano' must be integer, 'tmi' can be float
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype(int)
    df["tmi"] = pd.to_numeric(df["tmi"], errors="coerce")

    # 4) Write cleaned dataset to DATA_PROC/dfm.csv
    out = DATA_PROC / "dfm.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    print(f"✅ dfm saved at: {out}")


if __name__ == "__main__":
    run()