import unicodedata, pandas as pd, geopandas as gpd
from .paths import DATA_RAW, DATA_PROC

# -------------------------------------------------------------
# Text normalization:
# - Convert None → ""
# - Unicode NFKD decomposition (e.g., "ç" → "c")
# - Drop diacritics
# - Uppercase + trim
# This makes joins robust against accents/case/extra spaces.
# -------------------------------------------------------------
def norm(s):
    s = "" if s is None else str(s)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(ch)
    ).upper().strip()


def run(geo_mun="geojs-42-mun.json", mapping_csv="municipio_para_assoc.csv"):
    """
    Build a GeoJSON of Santa Catarina associations by dissolving municipalities
    into association polygons.

    Inputs (looked up under DATA_RAW/DATA_PROC):
      - geo_mun: a municipal boundaries GeoJSON/JSON (must include a name column)
      - mapping_csv: CSV with columns ['municipio_norm', 'assoc']

    Steps:
      1) Read municipal polygons and detect their name column.
      2) Normalize municipality names -> 'municipio_norm'.
      3) Read CSV mapping (municipio_norm -> assoc).
      4) Left-join: assign each municipality to an association.
      5) Validate: ensure no municipality is left unmapped.
      6) Reproject to WGS84 (EPSG:4326) if needed.
      7) Dissolve by 'assoc' to get association polygons.
      8) Simplify geometry for lighter GeoJSON.
      9) Save to DATA_PROC/sc_associacoes.geojson.
    """

    # 1) Load municipal boundaries (GeoDataFrame)
    gdf = gpd.read_file(DATA_RAW / geo_mun)

    # 2) Heuristically find the municipality name column
    candidate_cols = ["name", "NM_MUN", "NM_MUNICIP", "NM_MUNICIPIO", "nome", "municipio"]
    name_col = next((c for c in candidate_cols if c in gdf.columns), None)
    assert name_col, f"Municipality name column not found. Columns: {list(gdf.columns)}"

    # 3) Create a normalized key for robust joining
    gdf["municipio_norm"] = gdf[name_col].map(norm)

    # 4) Load mapping CSV: municipio_norm -> assoc (normalized association label)
    mapa = pd.read_csv(DATA_PROC / mapping_csv)

    # 5) Join mapping into geometry
    join = gdf.merge(mapa, on="municipio_norm", how="left")

    # 6) Validate missing associations (helps catch spelling issues up front)
    falta = join["assoc"].isna().sum()
    if falta:
        examples = join[join["assoc"].isna()][name_col].tolist()[:10]
        raise RuntimeError(f"{falta} municipality(ies) without association. Examples: {examples}")

    # 7) Ensure CRS is WGS84 (EPSG:4326) for web mapping compatibility
    if not join.crs or join.crs.to_epsg() != 4326:
        join = join.to_crs(epsg=4326)

    # 8) Dissolve municipalities by association to build association polygons
    g = join.dissolve(by="assoc", as_index=False)[["assoc", "geometry"]]

    # 9) Simplify geometry to reduce output size (tune tolerance as needed)
    #    - preserve_topology=True prevents self-intersections/artifacts
    g["geometry"] = g["geometry"].simplify(0.001, preserve_topology=True)

    # 10) Write GeoJSON to DATA_PROC
    out = DATA_PROC / "sc_associacoes.geojson"
    out.parent.mkdir(parents=True, exist_ok=True)
    g.to_file(out, driver="GeoJSON")
    print(f"✅ GeoJSON saved at: {out}")


if __name__ == "__main__":
    run()
