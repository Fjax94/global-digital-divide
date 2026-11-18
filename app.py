
import streamlit as st

st.set_page_config(
    page_title="Global Digital Divide",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Global Digital Divide Dashboard")

st.write(
    "Exploring internet access around the world "
    "using real data from the World Bank."
)

st.header("About This Project")

st.info(
    "This dashboard will analyze internet usage, "
    "compare countries, and visualize global trends."
)

st.success("Dashboard initialized successfully!")
