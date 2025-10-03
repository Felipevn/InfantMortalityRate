import unicodedata
import pandas as pd
import geopandas as gpd
from .paths import DATA_RAW, DATA_PROC

def norm(s: str) -> str:
    s = "" if s is None else str(s)
    return "".join(ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)).upper().strip()

def run(geo_mun: str = "geojs-42-mun.json", mapping_csv: str = "municipio_para_assoc.csv") -> None:
    gdf = gpd.read_file(DATA_RAW / geo_mun)      # id, name, description, geometry
    gdf["municipio_norm"] = gdf["name"].map(norm)
    mapa = pd.read_csv(DATA_PROC / mapping_csv)
    join = gdf.merge(mapa, on="municipio_norm", how="left")
    faltando = join["assoc"].isna().sum()
    if faltando:
        ex = join[join["assoc"].isna()]["name"].tolist()[:10]
        raise RuntimeError(f"{faltando} município(s) sem associação. Ex.: {ex}")
    if not join.crs or join.crs.to_epsg() != 4326:
        join = join.to_crs(epsg=4326)
    g = join.dissolve(by="assoc", as_index=False)[["assoc","geometry"]]
    g["geometry"] = g["geometry"].simplify(0.001, preserve_topology=True)
    out = DATA_PROC / "sc_associacoes.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)
    g.to_file(out, driver="GeoJSON")
    print(f"✅ geojson salvo em: {out}")

if __name__ == "__main__":
    run()
