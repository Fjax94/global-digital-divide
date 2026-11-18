from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Global Digital Divide",
    page_icon="🌍",
    layout="wide",
)

# Visual design: Modern Dark
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 0% 0%, #182b45 0%, #0a1020 55%, #080d18 100%);
    color: #edf3ff;
}
section[data-testid="stSidebar"] {background-color: #101b2d;}
div[data-testid="stMetric"] {
    background: #15243b;
    border: 1px solid #2b4160;
    border-radius: 14px;
    padding: 18px;
}
div[data-testid="stMetricValue"] {color: #5eead4;}
h1, h2, h3 {color: #f3f6ff;}
</style>
""", unsafe_allow_html=True)

COUNTRIES = {
    "IRQ": "Iraq", "ITA": "Italy", "BEL": "Belgium", "NLD": "Netherlands",
    "CAN": "Canada", "USA": "United States", "DEU": "Germany",
    "FRA": "France", "IND": "India", "ARE": "United Arab Emirates",
    "SAU": "Saudi Arabia", "JPN": "Japan",
}

@st.cache_data

def load_data():
    path = Path(__file__).resolve().parent / "internet_usage.csv"
    if not path.exists():
        raise FileNotFoundError("internet_usage.csv is missing from your GitHub repository.")
    raw = pd.read_csv(path)
    required = {"Entity", "Code", "Year"}
    if not required.issubset(raw.columns):
        raise ValueError("The CSV must contain Entity, Code, and Year columns.")
    value_cols = [c for c in raw.columns if c not in required]
    if not value_cols:
        raise ValueError("The CSV has no internet usage value column.")
    data = raw[["Entity", "Code", "Year", value_cols[0]]].copy()
    data.columns = ["Country", "Code", "Year", "Internet users (%)"]
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Internet users (%)"] = pd.to_numeric(
        data["Internet users (%)"], errors="coerce"
    )
    data = data.dropna(subset=["Year", "Internet users (%)"])
    data = data.loc[data["Code"].isin(COUNTRIES) & data["Year"].between(2000, 2025)].copy()
    data["Year"] = data["Year"].astype(int)
    data["Country"] = data["Code"].map(COUNTRIES)
    if data.empty:
        raise ValueError("No supported country records found in this file.")
    return data

st.title("🌍 Global Digital Divide")
st.markdown("**Internet access intelligence** · Country comparisons and historical trends")
st.caption("Indicator: Individuals using the Internet (% of population), 2000–2025")

try:
    data = load_data()
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Data could not be loaded: {error}")
    st.info("Upload the original Our World in Data CSV to the repository root as internet_usage.csv.")
    st.stop()

st.sidebar.header("⚙️ Explore data")
country_names = list(COUNTRIES.values())
selected = st.sidebar.multiselect(
    "Compare countries",
    country_names,
    default=["Iraq", "Italy", "Belgium"],
)
year_start, year_end = st.sidebar.slider(
    "Year range", min_value=2000, max_value=2025, value=(2000, 2025)
)

if not selected:
    st.warning("Choose at least one country from the sidebar.")
    st.stop()

filtered = data.loc[
    data["Country"].isin(selected) & data["Year"].between(year_start, year_end)
].copy()
if filtered.empty:
    st.warning("No observations for this selection. Try a wider year range.")
