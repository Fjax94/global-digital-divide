
import streamlit as st
import pandas as pd
import requests

# Page configuration
st.set_page_config(
    page_title="Global Digital Divide",
    page_icon="🌍",
    layout="wide"
)

# Dashboard title
st.title("🌍 Global Digital Divide Dashboard")
st.write(
    "Explore global internet access using real "
    "World Bank data from 2000 to 2025."
)

# Countries to analyze
COUNTRIES = [
    "IRQ", "ITA", "BEL", "NLD", "CAN", "USA",
    "DEU", "FRA", "IND", "ARE", "SAU", "JPN"
]

# Download data from the World Bank
@st.cache_data(ttl=86400)
def load_data():
    country_codes = ";".join(COUNTRIES)

    url = (
        "https://api.worldbank.org/v2/country/"
        f"{country_codes}/indicator/IT.NET.USER.ZS"
    )

    response = requests.get(
        url,
        params={
            "format": "json",
            "per_page": 1000,
            "date": "2000:2025"
        },
        timeout=(10, 60)
    )
    response.raise_for_status()

    result = response.json()

    if not isinstance(result, list) or not result[1]:
        raise ValueError("No data received from the World Bank.")

    rows = []

    for item in result[1]:
        if item["value"] is not None:
            rows.append({
                "Country": item["country"]["value"],
                "Year": int(item["date"]),
                "Internet users (%)": float(item["value"])
            })

    if not rows:
        raise ValueError("No valid observations found.")

    return pd.DataFrame(rows)


# Load the dataset
try:
    with st.spinner("Loading World Bank data..."):
        df = load_data()
except (requests.RequestException, ValueError, KeyError) as error:
    st.error(f"Unable to load data: {error}")
    st.stop()

# Country selection
st.subheader("🌐 Select Countries")

available = sorted(df["Country"].unique())

default_countries = [
    c for c in ["Iraq", "Italy", "Belgium"]
    if c in available
]

selected = st.multiselect(
    "Choose countries to compare:",
    options=available,
    default=default_countries
)

if not selected:
    st.warning("Please select at least one country.")
    st.stop()

filtered = df[df["Country"].isin(selected)].copy()

# Summary metrics
col1, col2 = st.columns(2)

with col1:
    st.metric("Selected Countries", len(selected))

with col2:
    st.metric("Available Data Points", len(filtered))

# Line chart
st.subheader("📈 Internet Usage Over Time")

chart_data = filtered.pivot(
    index="Year",
    columns="Country",
    values="Internet users (%)"
).sort_index()

st.line_chart(chart_data)

st.caption(
    "Percentage of individuals using the internet. "
    "Missing years are not estimated."
)

# Latest available figures
st.subheader("📊 Latest Available Data")

latest = (
    filtered.sort_values("Year")
    .groupby("Country")
    .tail(1)
    .sort_values("Internet users (%)", ascending=False)
)

st.dataframe(
    latest[["Country", "Year", "Internet users (%)"]],
    hide_index=True
)

# Download data
st.subheader("📥 Download Dataset")

csv = filtered.sort_values(
    ["Country", "Year"]
).to_csv(index=False)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="internet_usage_data.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "Data source: World Bank Open Data | "
    "Indicator IT.NET.USER.ZS"
)
