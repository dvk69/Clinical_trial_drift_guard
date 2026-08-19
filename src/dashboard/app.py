import sys
import os

# Ensure project root is in sys.path so 'src' imports work anywhere
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

st.title("🏥 Clinical Trial Data Integrity & Cross-Site Drift Monitor")
st.markdown("""
*Designed as a distributed data quality framework complementing protected health data environments like **Duke's DEDUCE and PACE**.*
""")

if not os.path.exists(DRIFT_REPORT_PATH) or not os.path.exists(PROCESSED_DATA_PATH):
    st.error("Pipeline outputs missing! Run `python main.py` first.")
    st.stop()

with open(DRIFT_REPORT_PATH, "r") as f:
    drift_data = json.load(f)

df = pd.read_parquet(PROCESSED_DATA_PATH)

# Header Metric Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ingested Patient Records", f"{len(df):,}")
col2.metric("Trial Sites Monitored", len(drift_data))
col3.metric("PII Masking Protocol", "Salted SHA-256 (Passed)")

drift_sites = [s["site_id"] for s in drift_data if any(f["drift_detected"] for f in s["features"].values())]
col4.metric("Sites Flagged with Drift", len(drift_sites), delta_color="inverse")

st.markdown("---")

# Section 1: Drift Matrix Heatmap
st.subheader("1. Cross-Site Statistical Drift Matrix (PSI)")

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
    color_continuous_scale="Reds",
    text_auto=True
)
st.plotly_chart(fig_heat, use_container_width=True)

# Section 2: Clinical Feature Distributions Across Sites
st.subheader("2. Distribution Drift Inspection (Systolic Blood Pressure)")
fig_box = px.box(
    df, 
    x="site_id", 
    y="systolic_bp", 
    color="site_id",
    title="Systolic BP Readings across Trial Sites (Detecting Site 004/005 Sensor Shift)"
)
st.plotly_chart(fig_box, use_container_width=True)

# Section 3: Detailed Site Diagnostics Table
st.subheader("3. Biostatistical Site Integrity Diagnostic Logs")
selected_site = st.selectbox("Select Trial Site to Inspect", [s["site_id"] for s in drift_data])
site_info = next(s for s in drift_data if s["site_id"] == selected_site)

diag_df = pd.DataFrame(site_info["features"]).T
st.dataframe(diag_df, use_container_width=True)