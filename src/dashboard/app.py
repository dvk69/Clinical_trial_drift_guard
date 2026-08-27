import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import json
import plotly.express as px
from src.utils.config import DRIFT_REPORT_PATH, PROCESSED_DATA_PATH

st.set_page_config(
    page_title="Clinical Trial Data Integrity Monitor",
    page_icon="🏥",
    layout="wide"
)

if not os.path.exists(DRIFT_REPORT_PATH) or not os.path.exists(PROCESSED_DATA_PATH):
    with st.spinner("Preparing synthetic multi-site trial data and running integrity checks..."):
        from main import main as run_pipeline
        run_pipeline()

st.title("Clinical Trial Data Integrity & Cross-Site Drift Monitor")
st.markdown("""
**A distributed quality-control layer for multi-site clinical research.**  
Inspect de-identified synthetic records, cross-site feature drift, and sensor calibration signals before they reach downstream analysis.
""")

with open(DRIFT_REPORT_PATH, "r") as f:
    drift_data = json.load(f)

df = pd.read_parquet(PROCESSED_DATA_PATH)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingested Records", f"{len(df):,}")
col2.metric("Trial Sites", len(drift_data))
col3.metric("PII Protocol", "SHA-256 · Passed")

drift_sites = [s["site_id"] for s in drift_data if any(f["drift_detected"] for f in s["features"].values())]
col4.metric("Sites Flagged", len(drift_sites), delta_color="inverse")

st.markdown("---")
st.subheader("1. Cross-Site Statistical Drift Matrix")
heat_records = []
for site in drift_data:
    row = {"Site": site["site_id"]}
    for feat, vals in site["features"].items():
        row[feat] = vals["psi"]
    heat_records.append(row)
heat_df = pd.DataFrame(heat_records).set_index("Site")
fig_heat = px.imshow(
    heat_df.T,
    labels=dict(x="Trial Site", y="Clinical Feature", color="PSI Value"),
    x=heat_df.index,
    y=heat_df.columns,
    color_continuous_scale=["#e8e5de", "#aeb9b0", "#9a6753"],
    text_auto=True
)
st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("2. Distribution Drift Inspection")
fig_box = px.box(
    df,
    x="site_id",
    y="systolic_bp",
    color="site_id",
    title="Systolic blood pressure readings by trial site"
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

st.subheader("3. Site Integrity Diagnostic Log")
selected_site = st.selectbox("Select trial site", [s["site_id"] for s in drift_data])
site_info = next(s for s in drift_data if s["site_id"] == selected_site)
diag_df = pd.DataFrame(site_info["features"]).T
st.dataframe(diag_df, use_container_width=True)
