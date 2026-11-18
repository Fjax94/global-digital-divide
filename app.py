"""Global Digital Divide | Modern Dark Streamlit dashboard.

Source: Our World in Data, "Share of the population using the Internet"
(original statistics from ITU / World Bank).

Place internet_usage.csv next to this app.py. The app uses a local snapshot,
so charts do not depend on remote APIs or unstable network connections.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# -----------------------------------------------------------------------------
# 1. Settings and design
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Digital Divide | Data Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).resolve().parent / "internet_usage.csv"
METRIC = "Internet users (%)"
REQUIRED_COLUMNS = {"Entity", "Code", "Year"}
POSSIBLE_METRIC_COLUMNS = (
    "Share of the population using the Internet",
    "Individuals using the Internet (% of population)",
    "Internet users (% of population)",
)
COLORS = [
    "#39d9c5", "#70a8ff", "#c39cff", "#ffbf69", "#ff7f9f",
    "#a1db77", "#68d2ff", "#f5a4d6", "#f5d76e", "#a7b7ff",
]

st.markdown(
    """
<style>
:root { color-scheme: dark; }
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #080f1d !important;
    color: #edf4ff;
}
.stApp {
    background: radial-gradient(ellipse at 14% 0%, #182943 0%, #0d182b 42%, #080f1d 100%) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #101d30 !important;
    border-right: 1px solid #263b56 !important;
}
.block-container { max-width: 1440px; padding-top: 2.0rem; padding-bottom: 2.8rem; }
h1, h2, h3, h4 { color: #f2f7ff !important; }
[data-testid="stMetric"] {
    background: #13253b;
    border: 1px solid #28415e;
    border-radius: 16px;
    padding: 16px 18px;
}
[data-testid="stMetricLabel"] { color: #a8bed8 !important; }
[data-testid="stMetricValue"] { color: #73eadb !important; }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 12px; }
.app-kicker {
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #65e2d4;
    font-size: .78rem;
    font-weight: 700;
    margin-bottom: .45rem;
}
.app-subtitle { color: #aabed9; font-size: 1.02rem; margin-bottom: 1.1rem; }
.section-note { color: #9db2ce; font-size: .87rem; margin-top: -.35rem; }
.source-note { color: #9caec7; font-size: .82rem; }
/* The track correctly moves left-to-right, but this deployment mirrors only
   BaseWeb's thumb layer. Mirror that layer back, leaving the fill untouched.
   The immediate thumb parent is targeted, not the track or the whole slider. */
[data-testid="stSlider"] [data-baseweb="slider"] div:has(> [role="slider"]) {
    transform: scaleX(-1);
    transform-origin: center center;
}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] > div {
    transform: scaleX(-1);
}
[data-testid="stSlider"] [data-baseweb="slider"],
[data-testid="stSlider"] [data-testid="stTickBar"] {
    direction: ltr;
}
.year-ends {
    display: flex;
    flex-direction: row;
    direction: ltr;
    justify-content: space-between;
    font-size: .82rem;
    color: #afc3db;
    margin-top: -.4rem;
    margin-bottom: .75rem;
}

@media (max-width: 700px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    [data-testid="stMetric"] { padding: 12px; }
}
</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. Load and validate the actual CSV (no API call, no invented observations)
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data(csv_path: str, modified_ns: int, size_bytes: int) -> pd.DataFrame:
    """Validate an OWID CSV; return one real observation per country/year."""
    _ = (modified_ns, size_bytes)  # Cache invalidation when the file changes.
    raw = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
    raw.columns = raw.columns.str.strip()

    missing = REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    metric_column = next(
        (name for name in POSSIBLE_METRIC_COLUMNS if name in raw.columns), None
    )
    if metric_column is None:
        alternatives = [name for name in raw.columns if name not in REQUIRED_COLUMNS]
        if len(alternatives) == 1:
            metric_column = alternatives[0]
        else:
            raise ValueError(
                "Could not find the internet usage column. "
                f"Available columns: {', '.join(raw.columns)}"
            )

    data = raw[["Entity", "Code", "Year", metric_column]].copy()
    data.columns = ["Country", "Code", "Year", METRIC]
    data["Code"] = data["Code"].astype("string").str.strip().str.upper()
    data["Country"] = data["Country"].astype("string").str.strip()
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data[METRIC] = pd.to_numeric(data[METRIC], errors="coerce")

    # OWID regional/world aggregates use non-ISO-3 identifiers: remove them.
    data = data[data["Code"].str.fullmatch(r"[A-Z]{3}", na=False)].copy()
    data = data.dropna(subset=["Country", "Code", "Year", METRIC])
    data = data[data[METRIC].between(0, 100)].copy()
    if data.empty:
        raise ValueError("No valid country observations were found in the CSV.")

    data["Year"] = data["Year"].astype(int)
    data = data.sort_values(["Code", "Year"]).drop_duplicates(
        subset=["Code", "Year"], keep="last"
    )
    return data.sort_values(["Country", "Year"]).reset_index(drop=True)


def latest_observed(data: pd.DataFrame, through_year: int) -> pd.DataFrame:
    """Use observed data only; never interpolate or fill missing years."""
    subset = data.loc[data["Year"] <= through_year].copy()
    if subset.empty:
        return subset
    return (
        subset.sort_values(["Code", "Year"])
        .drop_duplicates("Code", keep="last")
        .sort_values(METRIC, ascending=False)
        .reset_index(drop=True)
    )


def style_chart(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbe8fa", size=12),
        height=height,
        margin=dict(l=16, r=22, t=22, b=28),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#16283f", font_color="#f1f7ff"),
    )
    return fig


st.markdown(
    '<div class="app-kicker">DATA SCIENCE PORTFOLIO · INTERACTIVE ANALYTICS</div>',
    unsafe_allow_html=True,
)
st.title("🌍 Global Digital Divide")
st.markdown(
    '<div class="app-subtitle">Explore how internet access has changed around the world.</div>',
    unsafe_allow_html=True,
)

if not DATA_FILE.is_file():
    st.error("Missing dataset: `internet_usage.csv`.")
    st.info(
        "Add the original `internet_usage.csv` file to the same GitHub folder "
        "as `app.py`, then redeploy. The dashboard cannot show real observations "
        "without the dataset."
    )
    st.stop()

try:
    info = DATA_FILE.stat()
    data = load_data(str(DATA_FILE), info.st_mtime_ns, info.st_size)
except (OSError, UnicodeError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"Could not load `internet_usage.csv`: {exc}")
    st.info("Verify the filename and CSV headers, then commit the corrected CSV to GitHub.")
    st.stop()

min_year = int(data["Year"].min())
max_year = int(data["Year"].max())
country_options = sorted(data["Country"].unique().tolist())
# -----------------------------------------------------------------------------
# 3. Filters and a strictly left-to-right year timeline
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Explore data")
    selected_countries = st.multiselect(
        "Compare countries",
        options=country_options,
        default=[],
        key="country_picker_v2",
        max_selections=10,
        help="Choose up to 10 countries to compare.",
    )
    st.markdown("#### 🕒 Explore by year")
    if min_year < max_year:
        selected_year = st.slider(
            "Year",
            min_value=min_year,
            max_value=max_year,
            value=max_year,
            step=1,
            key="sidebar_year_v2",
            help="Move right for newer years, or left for older years.",
        )
    else:
        selected_year = min_year
        st.caption(f"Only {min_year} is available in this dataset.")
    st.markdown(
        f'<div class="year-ends" dir="ltr">'
        f'<span>{min_year} · Oldest</span>'
        f'<span>Newest · {max_year}</span>'
        f'</div>', unsafe_allow_html=True
    )
    st.caption(f"Showing observations through **{selected_year}**")

    st.divider()
    st.markdown("**Dataset**")
    st.caption("Internet users (% of population)")
    st.caption(f"Recorded period: {min_year}–{max_year}")
    st.caption(f"Countries with data: {data['Code'].nunique():,}")
    st.caption("Source: Our World in Data (ITU / World Bank)")
    st.caption("Offline CSV snapshot — no live API requests")

# -----------------------------------------------------------------------------
# 4. Summaries: use each country's latest actually reported observation
# -----------------------------------------------------------------------------
if not selected_countries:
    st.info(
        "👈 Select a country in **Compare countries** on the left to view its "
        "internet access history, statistics, and world map. "
        "Select more countries to compare them."
    )
    st.stop()

world_latest = latest_observed(data, selected_year)
selected_data = data.loc[
    data["Country"].isin(selected_countries) & (data["Year"] <= selected_year)
].copy()
if selected_data.empty:
    st.warning(
        "No reported observations for these countries by the selected year. "
        "Move the year slider to the right or choose another country."
    )
    st.stop()

selected_latest = latest_observed(selected_data, selected_year)

# Stable country-to-color mapping, reused for every categorical chart.
country_colors = {
    country: COLORS[i % len(COLORS)]
    for i, country in enumerate(sorted(selected_countries))
}

# Transparent growth calculations based only on actual first/last observations.
first_records = (
    selected_data.sort_values(["Code", "Year"])
    .drop_duplicates("Code", keep="first")
    [["Code", "Year", METRIC]]
    .rename(columns={"Year": "First year", METRIC: "First (%)"})
)
country_stats = (
    selected_latest[["Code", "Country", "Year", METRIC]]
    .rename(columns={"Year": "Last year", METRIC: "Latest (%)"})
    .merge(first_records, on="Code", how="left", validate="one_to_one")
)
country_stats["Change (pp)"] = (
    country_stats["Latest (%)"] - country_stats["First (%)"]
)
country_stats["Years between"] = (
    country_stats["Last year"] - country_stats["First year"]
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Selected countries", len(selected_countries))
k2.metric("Observations", f"{len(selected_data):,}")
k3.metric("Countries on map", f"{len(world_latest):,}")
k4.metric(
    "Selected-country average",
    f"{selected_latest[METRIC].mean():.1f}%" if not selected_latest.empty else "—",
    help="Unweighted mean of the latest recorded values for selected countries, not a global average.",
)

# Extra insights show percentage-point changes, never invented missing years.
top_access = country_stats.sort_values(
    ["Latest (%)", "Country"], ascending=[False, True]
).iloc[0]
top_growth = country_stats.sort_values(
    ["Change (pp)", "Country"], ascending=[False, True]
).iloc[0]
g1, g2, g3 = st.columns(3)
g1.metric(
    "Highest internet use",
    f"{top_access['Latest (%)']:.1f}%",
    help=f"{top_access['Country']} — reported {int(top_access['Last year'])}",
)
g2.metric(
    "Largest recorded increase",
    f"{top_growth['Change (pp)']:+.1f} pp",
    help=f"{top_growth['Country']} — first available to last available observation",
)
g3.metric(
    "Average recorded increase",
    f"{country_stats['Change (pp)'].mean():+.1f} pp",
    help="Unweighted average of selected countries' observed percentage-point changes.",
)
st.caption(
    "Growth = latest available internet-use percentage minus the first available "
    "percentage for each selected country. Periods differ by country; "
    "these are percentage-point changes, not annual growth rates."
)

# Timeline: always chronological left -> right.
st.markdown("### 📈 Internet access over time")
line = px.line(
    selected_data.sort_values(["Country", "Year"]),
    x="Year", y=METRIC, color="Country", markers=True,
    color_discrete_map=country_colors,
    hover_data={"Year": True, METRIC: ":.2f"},
)
line.update_traces(line=dict(width=3), marker=dict(size=5))
style_chart(line, height=400)
line.update_layout(hovermode="x unified")
line.update_xaxes(
    title_text="Year (oldest → newest)",
    autorange=False,
    range=[min_year - 0.5, max(selected_year, min_year + 1) + 0.5],
    dtick=max(1, (max_year - min_year) // 7),
    showgrid=False,
    zeroline=False,
)
line.update_yaxes(
    title_text="Population using the internet (%)",
    range=[0, 105], ticksuffix="%", gridcolor="#263a55", zeroline=False,
)
st.plotly_chart(line, use_container_width=True, theme=None)

left, right = st.columns(2, gap="large")
with left:
    st.markdown("### 📊 Latest reported values")
    bar_data = selected_latest.sort_values(METRIC, ascending=True)
    bars = px.bar(
        bar_data, x=METRIC, y="Country", orientation="h",
        color="Country", color_discrete_map=country_colors,
        text=METRIC,
    )
    bars.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    style_chart(bars, height=max(315, 48 * len(bar_data) + 115))
    bars.update_layout(showlegend=False, margin=dict(l=10, r=55, t=20, b=25))
    bars.update_xaxes(range=[0, 110], ticksuffix="%", showgrid=False, title_text="")
    bars.update_yaxes(title_text="")
    st.plotly_chart(bars, use_container_width=True, theme=None)

with right:
    st.markdown("### 📋 Country comparison")
    sort_choice = st.selectbox(
        "Sort countries by",
        [
            "Internet use · highest first",
            "Change · largest increase",
            "Latest reporting year",
            "Country · A to Z",
        ],
        key="country_table_sort_v2",
    )
    if sort_choice == "Change · largest increase":
        ranked = country_stats.sort_values(
            ["Change (pp)", "Country"], ascending=[False, True]
        )
    elif sort_choice == "Latest reporting year":
        ranked = country_stats.sort_values(
            ["Last year", "Country"], ascending=[False, True]
        )
    elif sort_choice == "Country · A to Z":
        ranked = country_stats.sort_values("Country")
    else:
        ranked = country_stats.sort_values(
            ["Latest (%)", "Country"], ascending=[False, True]
        )
    display = ranked[
        ["Country", "Latest (%)", "Last year", "Change (pp)", "First year", "First (%)"]
    ].copy()
    display[["Latest (%)", "Change (pp)", "First (%)"]] = display[
        ["Latest (%)", "Change (pp)", "First (%)"]
    ].round(2)
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.caption(
        "Latest year can vary by country. Change (pp) compares each country's "
        "first and latest observed percentages; missing years are never estimated."
    )

st.download_button(
    "⬇️ Download selected country data (CSV)",
    data=selected_data.sort_values(["Country", "Year"]).to_csv(index=False).encode("utf-8-sig"),
    file_name="digital_divide_selected_data.csv",
    mime="text/csv",
)

# -----------------------------------------------------------------------------
# 5. Map: all countries with available data through the selected year
# -----------------------------------------------------------------------------
st.markdown("### 🗺️ World map")
st.markdown(
    '<div class="section-note">Latest observed internet-use percentage per country '
    'through the selected year. Reporting years may differ.</div>',
    unsafe_allow_html=True,
)

if world_latest.empty:
    st.warning("No geographic observations exist before this year in the CSV.")
else:
    map_fig = go.Figure(
        go.Choropleth(
            locations=world_latest["Code"],
            z=world_latest[METRIC],
            text=world_latest["Country"],
            customdata=world_latest["Year"],
            locationmode="ISO-3",
            zmin=0, zmax=100,
            colorscale=[
                [0.0, "#1a2a49"], [0.25, "#315c91"],
                [0.55, "#259bad"], [0.80, "#42d4bd"], [1.0, "#a5f3db"],
            ],
            marker_line_color="#15263c",
            marker_line_width=0.35,
            colorbar=dict(
                title=dict(text="Internet use (%)"),
                tickfont=dict(color="#cbd9ea"),
                ticksuffix="%",
            ),
            hovertemplate=(
                "<b>%{text}</b><br>Internet use: %{z:.1f}%"
                "<br>Recorded year: %{customdata}<extra></extra>"
            ),
        )
    )
    style_chart(map_fig, height=480)
    map_fig.update_geos(
        showframe=False, showcoastlines=False, showland=True,
        landcolor="#1e304b", bgcolor="rgba(0,0,0,0)",
        projection_type="natural earth",
    )
    # Draw only a high-contrast country outline over the original country
    # colors. No value or geography is changed in the underlying map.
    map_fig.add_trace(
        go.Choropleth(
            locations=country_stats["Code"],
            z=country_stats["Latest (%)"],
            text=country_stats["Country"],
            customdata=country_stats["Last year"],
            locationmode="ISO-3",
            zmin=0, zmax=100,
            colorscale=[
                [0.0, "#1a2a49"], [0.25, "#315c91"],
                [0.55, "#259bad"], [0.80, "#42d4bd"], [1.0, "#a5f3db"],
            ],
            showscale=False,
            marker_line_color="#ffdf73",
            marker_line_width=2.6,
            hovertemplate=(
                "<b>%{text} · SELECTED</b><br>Internet use: %{z:.1f}%"
                "<br>Recorded year: %{customdata}<extra></extra>"
            ),
        )
    )
    map_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.caption("Selected countries are outlined in gold; others remain on the world map.")
    st.plotly_chart(map_fig, use_container_width=True, theme=None)

st.divider()
st.markdown(
    '<div class="source-note">Data source: Our World in Data — Individuals using '
    'the Internet (ITU / World Bank). A local CSV snapshot is used: the selected '
    'year is a cutoff, not a claim that every country reported in that year. '
    'The dashboard provides descriptive comparisons, not causal conclusions.</div>',
    unsafe_allow_html=True,
)
