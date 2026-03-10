
from pathlib import Path
import numpy as np
import pandas as pd

WATCH_ORDER = ["1st Watch", "2nd Watch", "3rd Watch"]


def load_calls(path: str | Path) -> pd.DataFrame:
    """Load the patrol call dataset from Excel."""
    df = pd.read_excel(path)
    return df


def _watch_from_hour(hour: int) -> str:
    if 0 <= hour < 8:
        return "1st Watch"
    if 8 <= hour < 16:
        return "2nd Watch"
    return "3rd Watch"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create district × watch demand and baseline staffing features."""
    d = df[df["call_district"].notna() & df["patrol_watch"].notna()].copy()
    d["district"] = d["call_district"].astype(int)
    d["watch"] = d["patrol_watch"].astype(str)
    d["priority"] = pd.to_numeric(d["call_priority"], errors="coerce").fillna(9).astype(int)
    d["service_secs"] = pd.to_numeric(
        d["disp_to_close_secs"].fillna(d["rec_to_close_secs"]), errors="coerce"
    ).clip(lower=0)
    d["officers_patrol"] = pd.to_numeric(d["officers_dispatched_patrol"], errors="coerce").fillna(0)
    d["hour"] = pd.to_numeric(d["call_hour_of_day"], errors="coerce").fillna(0).astype(int)
    d["watch_from_hour"] = d["hour"].apply(_watch_from_hour)

    pat = d[d["officers_patrol"] > 0].copy()
    pat["effective_officer_secs"] = pat["service_secs"].clip(upper=7200) * pat["officers_patrol"]

    agg = pat.groupby(["district", "watch"]).agg(
        patrol_calls=("eid", "count"),
        officer_hours_capped=("effective_officer_secs", lambda s: float(s.sum()) / 3600.0),
        p1=("priority", lambda s: int((s == 1).sum())),
        p2=("priority", lambda s: int((s == 2).sum())),
        p3=("priority", lambda s: int((s == 3).sum())),
        median_service_mins=("service_secs", lambda s: float(np.nanmedian(s)) / 60.0),
        mean_officers_per_call=("officers_patrol", "mean"),
        unique_units=("first_dispatch_patrol_unid", pd.Series.nunique),
    ).reset_index()

    hourly = (
        pat.groupby(["district", "watch_from_hour", "hour"])["first_dispatch_patrol_unid"]
        .nunique()
        .reset_index(name="hourly_units")
    )
    hourly_max = (
        hourly.groupby(["district", "watch_from_hour"])["hourly_units"]
        .max()
        .reset_index(name="max_hourly_units")
    )
    hourly_avg = (
        hourly.groupby(["district", "watch_from_hour"])["hourly_units"]
        .mean()
        .reset_index(name="avg_hourly_units")
    )

    feat = (
        agg.merge(hourly_max.rename(columns={"watch_from_hour": "watch"}), on=["district", "watch"])
        .merge(hourly_avg.rename(columns={"watch_from_hour": "watch"}), on=["district", "watch"])
        .sort_values(["watch", "district"])
        .reset_index(drop=True)
    )

    # Baseline proxy from average active units; lower bounded for officer safety / minimum coverage.
    feat["baseline_staff"] = feat["avg_hourly_units"].round().clip(lower=2).astype(int)

    # Demand proxies
    feat["workload_units"] = feat["officer_hours_capped"] / (8.0 * 0.70)
    feat["priority_units"] = (1.75 * feat["p1"] + 1.25 * feat["p2"] + 0.75 * feat["p3"]) / 8.0
    feat["concurrency_units"] = 0.85 * feat["max_hourly_units"]
    feat["required_units"] = feat[["workload_units", "priority_units", "concurrency_units"]].max(axis=1)

    # Higher penalty where high-priority volume is concentrated.
    feat["weight"] = 1.0 + 0.10 * feat["p1"] + 0.05 * feat["p2"]

    feat["baseline_shortage"] = np.maximum(feat["required_units"] - feat["baseline_staff"], 0.0)
    feat["coverage_baseline"] = feat["baseline_staff"] / feat["required_units"]
    return feat


def build_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize point data for district-level maps."""
    d = df[
        df["call_district"].notna()
        & df["latitude"].notna()
        & df["longitude"].notna()
        & df["officers_dispatched_patrol"].fillna(0).gt(0)
    ].copy()

    d["district"] = d["call_district"].astype(int)
    d["priority"] = pd.to_numeric(d["call_priority"], errors="coerce").fillna(9).astype(int)
    d["service_secs"] = pd.to_numeric(
        d["disp_to_close_secs"].fillna(d["rec_to_close_secs"]), errors="coerce"
    ).clip(lower=0)

    district_map = d.groupby("district").agg(
        latitude=("latitude", "median"),
        longitude=("longitude", "median"),
        patrol_calls=("eid", "count"),
        p1_calls=("priority", lambda s: int((s == 1).sum())),
        avg_service_mins=("service_secs", lambda s: float(np.nanmean(s)) / 60.0),
    ).reset_index()

    return district_map
