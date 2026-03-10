
from pathlib import Path
import json
from patrol_staffing.data_prep import load_calls, build_features, build_map_data
from patrol_staffing.optimization import optimize_staffing
from patrol_staffing.viz import make_heatmap, make_shortage_chart, make_district_map

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "raw" / "Patrol_POC.xlsx"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "results" / "figures"
RESULTS = ROOT / "results"

PROCESSED.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

def main() -> None:
    calls = load_calls(DATA_PATH)
    feat = build_features(calls)
    result, summary = optimize_staffing(feat)
    map_df = build_map_data(calls)

    feat.to_csv(PROCESSED / "patrol_features.csv", index=False)
    result.to_csv(RESULTS / "patrol_staffing_results.csv", index=False)
    map_df.to_csv(PROCESSED / "district_map_data.csv", index=False)
    with open(RESULTS / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    make_heatmap(result, FIGURES / "staff_change_heatmap.png")
    make_shortage_chart(result, FIGURES / "shortage_comparison.png")
    make_district_map(map_df, FIGURES / "district_call_intensity_map.html")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
