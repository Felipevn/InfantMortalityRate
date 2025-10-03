import unicodedata, pandas as pd, geopandas as gpd
from .paths import DATA_RAW, DATA_PROC
def norm(s): s="" if s is None else str(s); return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).upper().strip()
def run(geo_mun="geojs-42-mun.json", mapping_csv="municipio_para_assoc.csv"):
    gdf=gpd.read_file(DATA_RAW/geo_mun)
    name_col=next((c for c in ["name","NM_MUN","NM_MUNICIP","NM_MUNICIPIO","nome","municipio"] if c in gdf.columns),None)
    assert name_col, f"Coluna de nome não encontrada. Colunas: {list(gdf.columns)}"
    gdf["municipio_norm"]=gdf[name_col].map(norm)
    mapa=pd.read_csv(DATA_PROC/mapping_csv)
    join=gdf.merge(mapa,on="municipio_norm",how="left")
    falta=join["assoc"].isna().sum()
    if falta: raise RuntimeError(f"{falta} município(s) sem associação. Ex.: {join[join['assoc'].isna()][name_col].tolist()[:10]}")
    if not join.crs or join.crs.to_epsg()!=4326: join=join.to_crs(epsg=4326)
    g=join.dissolve(by="assoc",as_index=False)[["assoc","geometry"]]; g["geometry"]=g["geometry"].simplify(0.001, preserve_topology=True)
    out=DATA_PROC/"sc_associacoes.geojson"; out.parent.mkdir(parents=True,exist_ok=True); g.to_file(out,driver="GeoJSON")
    print(f"✅ geojson salvo em: {out}")
if __name__=="__main__": run()
