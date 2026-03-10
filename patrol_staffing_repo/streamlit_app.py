
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from patrol_staffing.data_prep import load_calls, build_features, build_map_data
from patrol_staffing.optimization import optimize_staffing

st.set_page_config(page_title="Patrol Staffing Optimization POC", layout="wide")

DATA_PATH = ROOT / "data" / "raw" / "Patrol_POC.xlsx"

@st.cache_data
def load_model_outputs():
    calls = load_calls(DATA_PATH)
    feat = build_features(calls)
    result, summary = optimize_staffing(feat)
    map_df = build_map_data(calls)
    return calls, result, summary, map_df

calls, result, summary, map_df = load_model_outputs()

st.title("Patrol Staff Deployment Optimization")
st.caption("District × watch mixed-integer staffing optimization built from Patrol_POC.xlsx")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Modeled patrol calls", f"{summary['records_modeled']:,}")
c2.metric("Baseline staff", summary["baseline_staff_total"])
c3.metric("Optimized staff", summary["optimized_staff_total"], delta=summary["optimized_staff_total"] - summary["baseline_staff_total"])
c4.metric("Weighted shortage reduction", f"{summary['weighted_shortage_reduction_pct']}%")

st.subheader("Optimization summary")
left, right = st.columns([1, 2])
with left:
    st.json(summary)
with right:
    chart = pd.DataFrame({
        "Scenario": ["Baseline", "Optimized"],
        "Weighted shortage": [
            summary["baseline_weighted_shortage_total"],
            summary["optimized_weighted_shortage_total"],
        ],
        "Shortage": [
            summary["baseline_shortage_total"],
            summary["optimized_shortage_total"],
        ],
    })
    fig = px.bar(chart.melt(id_vars="Scenario", var_name="Metric", value_name="Value"),
                 x="Scenario", y="Value", color="Metric", barmode="group",
                 title="Baseline vs optimized shortages")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Staff change heatmap")
heat = result.pivot(index="district", columns="watch", values="staff_change")[["1st Watch", "2nd Watch", "3rd Watch"]]
fig_heat = px.imshow(
    heat,
    text_auto=True,
    aspect="auto",
    title="Recommended staff changes by district and watch",
    labels=dict(x="Watch", y="District", color="Staff change"),
)
st.plotly_chart(fig_heat, use_container_width=True)

st.subheader("District call intensity map")
fig_map = px.scatter_map(
    map_df,
    lat="latitude",
    lon="longitude",
    size="patrol_calls",
    color="p1_calls",
    hover_name="district",
    hover_data={"avg_service_mins":":.1f", "latitude":False, "longitude":False},
    zoom=10,
    map_style="carto-positron",
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader("Scenario controls")
extra_total = st.slider("Extra flex officers", 0, 12, 6)
max_change = st.slider("Maximum change per district-watch", 0, 3, 1)
adj_result, adj_summary = optimize_staffing(build_features(calls), extra_total=extra_total, max_change=max_change)

col_a, col_b = st.columns(2)
with col_a:
    st.metric("Adjusted optimized staff", adj_summary["optimized_staff_total"])
with col_b:
    st.metric("Adjusted weighted shortage reduction", f"{adj_summary['weighted_shortage_reduction_pct']}%")

adj_chart = adj_result.copy()
adj_chart["cell"] = adj_chart["district"].astype(str) + " / " + adj_chart["watch"]
fig_adj = px.bar(adj_chart, x="cell", y=["baseline_shortage", "optimized_shortage"], barmode="group",
                 title="Shortage by district-watch under selected scenario")
st.plotly_chart(fig_adj, use_container_width=True)

st.subheader("Recommended staffing table")
st.dataframe(
    result[[
        "district", "watch", "patrol_calls", "p1", "p2", "p3",
        "baseline_staff", "optimized_staff", "staff_change",
        "required_units", "baseline_shortage", "optimized_shortage"
    ]].sort_values(["watch", "district"]),
    use_container_width=True,
)
