import unicodedata, pandas as pd
from .paths import DATA_RAW, DATA_PROC
def norm(s): s="" if s is None else str(s); return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).upper().strip()
def run(xlsx="mortalidade.xlsx"):
    df=pd.read_excel(DATA_RAW/xlsx).rename(columns={"Região":"assoc","Ano":"ano","Mortalidade":"tmi"})
    df["assoc"]=df["assoc"].map(norm); df["ano"]=pd.to_numeric(df["ano"],errors="coerce").astype(int); df["tmi"]=pd.to_numeric(df["tmi"],errors="coerce")
    out=DATA_PROC/"dfm.csv"; out.parent.mkdir(parents=True,exist_ok=True); df.to_csv(out,index=False)
    print(f"✅ dfm salvo em: {out}")
if __name__=="__main__": run()
