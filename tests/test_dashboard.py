"""Smoke and regression checks for the public Streamlit dashboard."""
from pathlib import Path
import ast
import pandas as pd
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "internet_usage.csv"
APP = ROOT / "app.py"

def test_python_syntax_and_features():
    source = APP.read_text(encoding="utf-8")
    ast.parse(source, filename=str(APP))
    assert "color_discrete_map=country_colors" in source
    assert 'marker_line_color="#ffdf73"' in source
    assert '"Change (pp)"' in source
    assert "country_table_sort_v2" in source

def test_real_data_is_valid_and_growth_is_reproducible():
    raw = pd.read_csv(CSV)
    assert set(["Entity", "Code", "Year", "Share of the population using the Internet"]).issubset(raw.columns)
    raw = raw[raw["Entity"].isin(["Albania", "Cuba", "Costa Rica"]) & (raw["Year"] <= 2015)]
    assert len(raw) == 69
    assert raw["Year"].min() == 1990
    latest = raw.sort_values("Year").drop_duplicates("Code", keep="last").set_index("Entity")
    first = raw.sort_values("Year").drop_duplicates("Code", keep="first").set_index("Entity")
    metric = "Share of the population using the Internet"
    assert round(float(latest.loc["Albania", metric] - first.loc["Albania", metric]), 1) == 56.9
    assert round(float(latest.loc["Costa Rica", metric]), 2) == 59.76

def test_streamlit_starts_empty_and_renders_selected_countries():
    app = AppTest.from_file(str(APP), default_timeout=90).run()
    assert not app.exception, [x.message for x in app.exception]
    assert len(app.multiselect) == 1
    assert app.multiselect[0].value == []
    assert len(app.slider) == 1

    app.multiselect[0].set_value(["Albania", "Cuba", "Costa Rica"]).run()
    app.slider[0].set_value(2015).run()
    assert not app.exception, [x.message for x in app.exception]
    assert any(metric.label == "Selected countries" and str(metric.value) == "3" for metric in app.metric)
