
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def make_heatmap(result: pd.DataFrame, output_path: str | Path) -> None:
    pivot = result.pivot(index="district", columns="watch", values="staff_change")
    pivot = pivot[["1st Watch", "2nd Watch", "3rd Watch"]]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Recommended staff change by district and watch")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, int(pivot.iloc[i, j]), ha="center", va="center")
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def make_shortage_chart(result: pd.DataFrame, output_path: str | Path) -> None:
    chart = result.copy()
    chart["cell"] = chart["district"].astype(str) + " / " + chart["watch"]
    chart = chart.sort_values(["watch", "district"])
    fig, ax = plt.subplots(figsize=(10, 5))
    idx = range(len(chart))
    ax.bar([i - 0.2 for i in idx], chart["baseline_shortage"], width=0.4, label="Baseline")
    ax.bar([i + 0.2 for i in idx], chart["optimized_shortage"], width=0.4, label="Optimized")
    ax.set_xticks(list(idx))
    ax.set_xticklabels(chart["cell"], rotation=45, ha="right")
    ax.set_ylabel("Shortage units")
    ax.set_title("Baseline vs optimized shortage")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def make_district_map(map_df: pd.DataFrame, output_path: str | Path) -> None:
    fig = px.scatter_map(
        map_df,
        lat="latitude",
        lon="longitude",
        size="patrol_calls",
        hover_name="district",
        hover_data={"p1_calls": True, "avg_service_mins": ":.1f", "latitude": False, "longitude": False},
        zoom=10,
        map_style="carto-positron",
        title="District call intensity map"
    )
    fig.write_html(str(output_path), include_plotlyjs="cdn")
