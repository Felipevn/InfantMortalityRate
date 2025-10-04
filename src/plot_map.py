import json
import pandas as pd
import plotly.express as px
from .paths import DATA_PROC, DOCS

def run(geojson: str = "sc_associacoes.geojson", dfm_csv: str = "dfm.csv") -> None:
    dfm = pd.read_csv(DATA_PROC / dfm_csv)

    with open(DATA_PROC / geojson, "r", encoding="utf-8") as f:
        gjson = json.load(f)

    vmin, vmax = float(dfm["tmi"].min()), float(dfm["tmi"].max())

    fig = px.choropleth(
        dfm.sort_values("ano"),
        geojson=gjson,
        locations="assoc",
        featureidkey="properties.assoc",
        color="tmi",
        animation_frame="ano",          # <- use 'ano'
        color_continuous_scale="Reds",
        range_color=[vmin, vmax],
        labels={"tmi": "Infant mortality (‰)"},
        title="Infant Mortality Rate(IMR) — Santa Catarina (associations)",
    )

    # --- Somente slider (sem botões/play) ---
    fig.layout.updatemenus = []  # remove qualquer botão de play/pause

    # Ajustes do slider
    if fig.layout.sliders:
        for s in fig.layout.sliders:
            s.transition.duration = 0          # troca imediata ao arrastar
            s.currentvalue.prefix = "Year: "
            # opcional: dar um respiro na base do gráfico pro slider
            s.pad = dict(t=30)

    # Aparência/hover
    fig.update_traces(
        hovertemplate="<b>%{location}</b><br>Ano: %{animation_group}<br>TMI: %{z:.2f}‰<extra></extra>"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=20))

    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / "dashboard_sc.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"✅ dashboard salvo em: {out}")

if __name__ == "__main__":
    run()

