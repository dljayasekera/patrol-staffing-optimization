
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds

WATCH_ORDER = ["1st Watch", "2nd Watch", "3rd Watch"]


def optimize_staffing(
    feat: pd.DataFrame,
    extra_total: int = 6,
    max_change: int = 1,
    min_staff: int = 2,
    max_staff: int = 9,
    watch_flex: int = 2,
) -> tuple[pd.DataFrame, dict]:
    """
    Solve a mixed-integer optimization model for district × watch staffing.

    Decision variables
    ------------------
    x[i]         integer optimized staffing level
    s[i]         shortage slack if x[i] < required_units[i]
    dev_pos[i]   positive movement from baseline
    dev_neg[i]   negative movement from baseline

    Objective
    ---------
    Minimize:
        0.5 * x[i]
      + weight[i] * s[i]
      + 0.15 * dev_pos[i]
      + 0.15 * dev_neg[i]

    This favors reducing high-priority shortages while keeping plans realistic and
    avoiding unnecessary staff growth or reshuffling.
    """
    feat = feat.copy().reset_index(drop=True)
    n = len(feat)
    m = 4 * n
    base = feat["baseline_staff"].to_numpy(dtype=float)
    required = feat["required_units"].to_numpy(dtype=float)
    weights = feat["weight"].to_numpy(dtype=float)

    # variable order: x, shortage, dev_pos, dev_neg
    c = np.zeros(m)
    c[:n] = 0.5
    c[n:2 * n] = weights
    c[2 * n:3 * n] = 0.15
    c[3 * n:4 * n] = 0.15

    integrality = np.zeros(m, dtype=int)
    integrality[:n] = 1

    lb = np.zeros(m)
    ub = np.full(m, np.inf)
    lb[:n] = np.maximum(min_staff, base - max_change)
    ub[:n] = np.minimum(max_staff, base + max_change)

    A = []
    bl = []
    bu = []

    # shortage + staffing >= required
    row = np.zeros((n, m))
    for i in range(n):
        row[i, i] = 1.0
        row[i, n + i] = 1.0
    A.append(row)
    bl.extend(required.tolist())
    bu.extend([np.inf] * n)

    # staffing - dev_pos + dev_neg = baseline
    row = np.zeros((n, m))
    for i in range(n):
        row[i, i] = 1.0
        row[i, 2 * n + i] = -1.0
        row[i, 3 * n + i] = 1.0
    A.append(row)
    bl.extend(base.tolist())
    bu.extend(base.tolist())

    # watch totals can flex within a narrow band
    for watch, total in feat.groupby("watch")["baseline_staff"].sum().items():
        row = np.zeros(m)
        mask = feat.index[feat["watch"] == watch]
        row[mask] = 1.0
        A.append(row.reshape(1, -1))
        bl.append(max(float(total) - watch_flex, 0.0))
        bu.append(float(total) + watch_flex)

    # overall budget
    row = np.zeros(m)
    row[:n] = 1.0
    A.append(row.reshape(1, -1))
    bl.append(0.0)
    bu.append(float(base.sum()) + float(extra_total))

    result = milp(
        c=c,
        integrality=integrality,
        bounds=Bounds(lb, ub),
        constraints=LinearConstraint(np.vstack(A), bl, bu),
    )
    if not result.success:
        raise RuntimeError(result.message)

    feat["optimized_staff"] = np.round(result.x[:n]).astype(int)
    feat["optimized_shortage"] = np.maximum(result.x[n:2 * n], 0.0)
    feat["staff_change"] = feat["optimized_staff"] - feat["baseline_staff"]
    feat["coverage_optimized"] = feat["optimized_staff"] / feat["required_units"]
    feat["weighted_shortage_baseline"] = feat["baseline_shortage"] * feat["weight"]
    feat["weighted_shortage_optimized"] = feat["optimized_shortage"] * feat["weight"]

    summary = summarize_results(feat)
    return feat, summary


def summarize_results(result: pd.DataFrame) -> dict:
    base_short = float(result["baseline_shortage"].sum())
    opt_short = float(result["optimized_shortage"].sum())
    base_w = float(result["weighted_shortage_baseline"].sum())
    opt_w = float(result["weighted_shortage_optimized"].sum())

    summary = {
        "records_modeled": int(result["patrol_calls"].sum()),
        "district_watch_cells": int(len(result)),
        "baseline_staff_total": int(result["baseline_staff"].sum()),
        "optimized_staff_total": int(result["optimized_staff"].sum()),
        "baseline_shortage_total": round(base_short, 2),
        "optimized_shortage_total": round(opt_short, 2),
        "baseline_weighted_shortage_total": round(base_w, 2),
        "optimized_weighted_shortage_total": round(opt_w, 2),
        "shortage_reduction_pct": round(100.0 * (base_short - opt_short) / base_short, 1) if base_short else 0.0,
        "weighted_shortage_reduction_pct": round(100.0 * (base_w - opt_w) / base_w, 1) if base_w else 0.0,
    }
    return summary
