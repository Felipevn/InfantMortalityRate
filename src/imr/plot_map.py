import json
import pandas as pd
import plotly.express as px
from .paths import DATA_PROC, DOCS

def run(geojson: str = "sc_associacoes.geojson", dfm_csv: str = "dfm.csv") -> None:
    """
    Build an animated (by year) choropleth for Santa Catarina associations.

    Inputs (looked up under DATA_PROC):
      - dfm_csv: CSV with columns at least ['assoc', 'ano', 'tmi']
      - geojson: GeoJSON whose features have properties.assoc matching df['assoc']

    Output:
      - DOCS/dashboard_sc.html  (self-contained HTML using Plotly via CDN)
    """

    # 1) Load the table of metrics (one row per association & year).
    dfm = pd.read_csv(DATA_PROC / dfm_csv)

    # 2) Load the GeoJSON defining the association polygons.
    with open(DATA_PROC / geojson, "r", encoding="utf-8") as f:
        gjson = json.load(f)

    # 3) Fix the color scale across all frames (years) so the colors remain comparable.
    vmin, vmax = float(dfm["tmi"].min()), float(dfm["tmi"].max())

    # 4) Build the choropleth:
    #    - locations: values from dfm['assoc'] (must match GeoJSON property below)
    #    - featureidkey: where to look inside the GeoJSON to match 'locations'
    #    - color: the metric to paint each polygon
    #    - animation_frame: creates the YEAR slider (no play/pause buttons)
    fig = px.choropleth(
        dfm.sort_values("ano"),            # ensure frames are in chronological order
        geojson=gjson,                     # polygon geometry
        locations="assoc",                 # key in the dataframe
        featureidkey="properties.assoc",   # key inside the GeoJSON features
        color="tmi",                       # metric to color by
        animation_frame="ano",             # <-- year slider
        color_continuous_scale="Reds",     # color palette
        range_color=[vmin, vmax],          # fixed color range across frames
        labels={"tmi": "Infant mortality (‰)"},
        title="Infant Mortality Rate (IMR) — Santa Catarina (associations)",
    )

    # 5) Keep ONLY the slider: remove Plotly's default Play/Pause controls.
    #    (Some Plotly versions add updatemenus with play/pause; we clear them.)
    fig.layout.updatemenus = []

    # 6) Slider polish: instant transitions, prefix label, a bit of top padding.
    if fig.layout.sliders:
        for s in fig.layout.sliders:
            s.transition.duration = 0        # switch frames instantly while dragging
            s.currentvalue.prefix = "Year: " # "Year: 2019"
            s.pad = dict(t=30)               # space above the slider

    # 7) Tooltip/hover template:
    #    - %{location} is the 'assoc' (from the dataframe)
    #    - %{animation_group} is the frame key (year)
    #    - %{z} is the colored value (tmi)
    fig.update_traces(
        hovertemplate="<b>%{location}</b>"
                      "<br>Year: %{animation_group}"
                      "<br>IMR: %{z:.2f}‰"
                      "<extra></extra>"
    )

    # 8) Fit the view to the polygons and hide axes/graticules for a clean map.
    fig.update_geos(fitbounds="locations", visible=False)

    # 9) Trim margins so the figure uses space efficiently.
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=20))

    # 10) Export as a lightweight HTML (loads Plotly from CDN).
    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / "dashboard_sc.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"✅ dashboard saved at: {out}")

if __name__ == "__main__":
    run()