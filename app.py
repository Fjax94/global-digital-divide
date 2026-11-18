"""Global Digital Divide — an interactive, reproducible country dashboard.

Data: Our World in Data's Internet usage series (ITU / World Bank).
The app reads internet_usage.csv locally and never requires a live API request.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Global Digital Divide | Data Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Modern Dark design -----------------------------------------------------
st.markdown(
    """
    <style>
      .stApp {
        background: radial-gradient(ellipse at 16% 0%, #142840 0%, #0b1424 45%, #080f1d 100%);
        color: #e8effc;
      }
      section[data-testid="stSidebar"] {
        background: #101c30;
        border-right: 1px solid #243b56;
      }
      .block-container { padding-top: 2.3rem; padding-bottom: 3rem; }
      h1, h2, h3 { color: #f1f6ff !important; }
      div[data-testid="stMetric"] {
        background: #15263c;
        border: 1px solid #29425e;
        border-radius: 14px;
        padding: 14px 18px;
      }
      div[data-testid="stMetricLabel"] { color: #aebed6; }
      div[data-testid="stMetricValue"] { color: #69e3d3; }
      .app-kicker { color: #60e3d5; font-size: .85rem; font-weight: 650; letter-spacing: .13em; }
      .app-subtitle { color: #abbdd6; font-size: 1rem; margin-top: -.4rem; }
      .source-note { color: #9eafc8; font-size: .86rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA_FILE = Path(__file__).resolve().parent / "internet_usage.csv"
METRIC = "Internet users (%)"
REQUIRED_COLUMNS = {"Entity", "Code", "Year"}
PREFERRED_METRIC_COLUMN = "Share of the population using the Internet"
CHART_COLORS = [
    "#62dfcf", "#61aaff", "#c394fa", "#fbbf67", "#ff7f9c",
    "#9fdb71", "#f48fbf", "#77c8fd", "#efd46a", "#bcaaff",
]


@st.cache_data(show_spinner=False)
def load_data(path_str: str, file_mtime: float) -> pd.DataFrame:
    """Read the bundled CSV and validate its schema and numeric values."""
    raw = pd.read_csv(path_str, encoding="utf-8-sig", low_memory=False)
    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing))}")

    if PREFERRED_METRIC_COLUMN in raw.columns:
        value_col = PREFERRED_METRIC_COLUMN
    else:
        candidates = [c for c in raw.columns if c not in REQUIRED_COLUMNS]
        if len(candidates) != 1:
            raise ValueError("Could not identify the internet-usage percentage column.")
        value_col = candidates[0]

    data = raw[["Entity", "Code", "Year", value_col]].copy()
    data.columns = ["Country", "Code", "Year", METRIC]
    data["Code"] = data["Code"].astype("string")
    # OWID also publishes regional aggregates; exclude them from the country map.
    data = data[data["Code"].str.fullmatch(r"[A-Z]{3}", na=False)].copy()
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data[METRIC] = pd.to_numeric(data[METRIC], errors="coerce")
    data = data.dropna(subset=["Country", "Year", METRIC])
    data = data[data[METRIC].between(0, 100)].copy()
    data["Year"] = data["Year"].astype(int)
    data = data.sort_values("Year").drop_duplicates(["Code", "Year"], keep="last")

    if data.empty:
        raise ValueError("CSV contains no valid country internet-use observations.")
    return data


@st.cache_data(show_spinner=False)
def latest_by_country(data: pd.DataFrame, end_year: int) -> pd.DataFrame:
    """Last *observed* value through end_year (no imputation)."""
    within_period = data[data["Year"] <= end_year]
    return (within_period.sort_values("Year")
            .drop_duplicates("Code", keep="last")
            .sort_values(METRIC, ascending=False)
            .copy())


st.markdown('<div class="app-kicker">DATA SCIENCE PORTFOLIO · INTERACTIVE ANALYTICS</div>',
            unsafe_allow_html=True)
st.title("🌍 Global Digital Divide")
st.markdown('<div class="app-subtitle">Explore how internet access has changed across countries.</div>',
            unsafe_allow_html=True)

if not DATA_FILE.exists():
    st.error("The dataset `internet_usage.csv` is missing. Upload it next to `app.py` on GitHub.")
    st.stop()

try:
    data = load_data(str(DATA_FILE), DATA_FILE.stat().st_mtime)
except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Could not read `internet_usage.csv`: {exc}")
    st.stop()

min_year, max_year = int(data["Year"].min()), int(data["Year"].max())
countries = sorted(data["Country"].unique().tolist())
default_countries = [name for name in ["Iraq", "Italy", "Belgium"] if name in countries]

with st.sidebar:
    st.header("⚙️ Explore data")
    selected = st.multiselect(
        "Compare countries", options=countries,
        default=default_countries, max_selections=10,
        help="Choose up to 10 countries for a readable comparison.",
    )
    year_start, year_end = st.slider(
        "Year range", min_value=min_year, max_value=max_year,
        value=(max(min_year, 2000), max_year), step=1,
    )
    st.caption(f"Dataset coverage: {min_year}–{max_year}. This is a saved CSV snapshot, not a live feed.")
    st.divider()
    st.markdown("**Data:** Individuals using the Internet (% of population)")
    st.caption("Source: ITU / World Bank, published via Our World in Data.")

st.caption(f"Data snapshot covers years {min_year}–{max_year}; country reporting years may differ.")

if not selected:
    st.info("Select at least one country in the left sidebar to display the dashboard.")
    st.stop()

filtered = data[
    data["Country"].isin(selected) & data["Year"].between(year_start, year_end)
].copy()
if filtered.empty:
    st.warning("No reported data for those countries and dates. Try a wider year range.")
    st.stop()

latest_selected = latest_by_country(filtered, year_end)
world_latest = latest_by_country(data, year_end)

# --- KPI row ----------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Countries selected", len(selected))
kpi2.metric("Data observations", f"{len(filtered):,}")
kpi3.metric("Most recent year", int(latest_selected["Year"].max()))
kpi4.metric("Global countries shown", f"{len(world_latest):,}")

st.markdown("### 📈 Internet access over time")
line_fig = px.line(
    filtered.sort_values("Year"), x="Year", y=METRIC,
    color="Country", markers=True, color_discrete_sequence=CHART_COLORS,
    hover_data={METRIC: ":.2f", "Year": True},
)
line_fig.update_traces(line_width=3, marker_size=5)
line_fig.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)", font_color="#d8e5f5",
    margin=dict(l=20, r=20, t=18, b=20), height=390,
    legend_title_text="", hovermode="x unified",
    xaxis=dict(dtick=5, showgrid=False),
    yaxis=dict(range=[0, 105], ticksuffix="%", gridcolor="#24354c"),
)
st.plotly_chart(line_fig, use_container_width=True)

left, right = st.columns([1, 1], gap="large")
with left:
    st.markdown("### 📊 Latest reported values")
    bars = px.bar(
        latest_selected.sort_values(METRIC), x=METRIC, y="Country",
        orientation="h", color="Country", color_discrete_sequence=CHART_COLORS,
        text=METRIC,
    )
    bars.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    bars.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font_color="#d8e5f5",
        showlegend=False, height=350,
        margin=dict(l=5, r=55, t=10, b=15),
        xaxis=dict(range=[0, 110], ticksuffix="%", showgrid=False),
        yaxis=dict(title=""),
    )
    st.plotly_chart(bars, use_container_width=True)

with right:
    st.markdown("### 📋 Country comparison")
    table = latest_selected[["Country", "Year", METRIC]].copy()
    table[METRIC] = table[METRIC].round(2)
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.caption("Each country shows its latest *available* year within your selection; missing years are never estimated.")

st.markdown("### 🗺️ World map")
st.caption(f"Latest available observation per country through {year_end}; reporting years may vary.")
map_fig = go.Figure(go.Choropleth(
    locations=world_latest["Code"], z=world_latest[METRIC],
    text=world_latest["Country"], customdata=world_latest["Year"],
    locationmode="ISO-3", zmin=0, zmax=100,
    colorscale=[[0, "#182a4e"], [0.28, "#316fa2"], [0.65, "#3fc5c0"], [1, "#a1f7c8"]],
    marker_line_color="#17273c", marker_line_width=0.35,
    colorbar=dict(title="Internet use (%)", tickcolor="#b3c4d9", tickfont_color="#cbd9ea"),
    hovertemplate="<b>%{text}</b><br>%{z:.1f}% using internet<br>Reported: %{customdata}<extra></extra>",
))
map_fig.update_geos(showframe=False, showcoastlines=False, showland=True,
                    landcolor="#203048", bgcolor="rgba(0,0,0,0)",
                    projection_type="natural earth")
map_fig.update_layout(template="plotly_dark", height=470,
                      paper_bgcolor="rgba(0,0,0,0)",
                      margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(map_fig, use_container_width=True)

st.download_button(
    "⬇️ Download selected country data (CSV)",
    data=filtered.sort_values(["Country", "Year"]).to_csv(index=False).encode("utf-8"),
    file_name="digital_divide_selected_data.csv", mime="text/csv",
)
st.divider()
st.markdown(
    '<div class="source-note">Data source: Our World in Data — Individuals using the Internet '
    '(ITU / World Bank WDI). Offline snapshot in the GitHub repository; no live API calls. '
    'This dashboard provides descriptive analysis, not causal claims.</div>',
    unsafe_allow_html=True,
)
