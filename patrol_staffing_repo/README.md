# Patrol Staff Deployment Optimization

A GitHub-ready **operations research / public-safety analytics** project that converts historical patrol dispatch data into a **district × watch staffing optimization model**, an interactive **Streamlit dashboard**, reusable **Python modules**, and a **notebook walkthrough**.

This project is designed to demonstrate the kind of work expected from a **Senior Operations Research Scientist**: turning messy operational data into mathematical models, decision-support tools, and production-friendly analytics artifacts.

## Business problem

Police agencies must decide how many patrol officers to assign by district and watch while balancing:

- priority-call coverage
- workload pressure
- concurrency of active patrol units
- staffing limits
- realistic schedule changes

This repository uses the attached `Patrol_POC.xlsx` dataset to estimate demand pressure in each district-watch cell and solve a constrained **mixed-integer optimization** model for a better staffing plan.

## Repo contents

```text
patrol_staffing_repo/
├── data/
│   ├── raw/Patrol_POC.xlsx
│   └── processed/
│       ├── patrol_features.csv
│       └── district_map_data.csv
├── notebooks/
│   └── 01_patrol_staffing_poc.ipynb
├── results/
│   ├── patrol_staffing_results.csv
│   ├── summary.json
│   └── figures/
│       ├── staff_change_heatmap.png
│       ├── shortage_comparison.png
│       └── district_call_intensity_map.html
├── src/
│   ├── patrol_staffing/
│   │   ├── data_prep.py
│   │   ├── optimization.py
│   │   └── viz.py
│   └── run_pipeline.py
├── streamlit_app.py
├── requirements.txt
└── Dockerfile
```

## Optimization model

### Decision variables

For each district-watch cell \(i\):

- \(x_i\): integer officers assigned
- \(s_i\): shortage slack if staffing is below required demand
- \(d_i^+\), \(d_i^-\): positive/negative deviation from the baseline staffing proxy

### Objective

\[
\min \sum_i \left(0.5x_i + w_is_i + 0.15d_i^+ + 0.15d_i^- \right)
\]

The objective penalizes:
- shortages, especially in high-priority areas
- unnecessary staff growth
- large deviations from the current staffing pattern

### Demand proxy

Each district-watch demand requirement is estimated as:

\[
r_i = \max\left(
\frac{\text{capped officer hours}}{8 \times 0.70},
\frac{1.75P1 + 1.25P2 + 0.75P3}{8},
0.85 \times \text{max hourly active patrol units}
\right)
\]

This combines three operational signals:

1. **Workload units**: officer time tied up on calls  
2. **Priority units**: weighted importance of priority 1, 2, and 3 calls  
3. **Concurrency units**: the peak number of distinct patrol units active within the watch  

### Constraints

- integer staffing assignments
- at least 2 officers in each district-watch cell
- each district-watch may move by at most ±1 officer from baseline
- each watch total may flex by at most ±2 officers
- total staffing can increase by at most 6 flex officers above baseline

## Results from the attached file

Using the uploaded Excel file, the model produced:

- **Modeled patrol-dispatched calls:** 697
- **District-watch cells:** 12
- **Baseline staffing proxy:** 54
- **Optimized staffing plan:** 60
- **Baseline total shortage:** 69.36
- **Optimized total shortage:** 63.36
- **Baseline weighted shortage:** 297.27
- **Optimized weighted shortage:** 270.37
- **Total shortage reduction:** 8.7%
- **Weighted shortage reduction:** 9.0%

### Operational recommendation

The model recommends:

- adding staff mainly to **Districts 1 and 2 across all three watches**
- adding one slot to **District 3 / 3rd Watch**
- trimming one slot from **District 4 / 3rd Watch**

This pattern suggests the greatest shortage pressure is concentrated in the core patrol footprint represented by **Districts 1 and 2**, with additional late-watch pressure in **District 3**.

## Charts and maps

This repo includes:

- **staff change heatmap** for district-watch reallocations
- **baseline vs optimized shortage chart**
- **district call intensity map** built from median latitude/longitude by district

## How to run

### Local Python run

```bash
pip install -r requirements.txt
PYTHONPATH=src python src/run_pipeline.py
streamlit run streamlit_app.py
```

### Docker run

```bash
docker build -t patrol-staffing-poc .
docker run -p 8501:8501 patrol-staffing-poc
```

Then open the local Streamlit address in your browser.

## Why this project is strong for interviews

This project demonstrates:

- mixed-integer optimization
- demand modeling from operational data
- public-safety domain translation
- scenario analysis with controllable staffing assumptions
- dashboarding and decision support
- GitHub-ready technical communication

## Resume-ready project summary

**Patrol Staff Deployment Optimization | Python, SciPy MILP, Pandas, Streamlit, Plotly**  
Built a district × watch patrol staffing optimization model from CAD dispatch data to improve officer deployment under workload, priority, and concurrency constraints. Engineered demand proxies from 697 patrol-dispatched calls and solved a mixed-integer program that reduced total modeled shortage by **8.7%** and weighted shortage by **9.0%** while preserving realistic staffing movement limits. Packaged the solution as reusable Python modules, a notebook, an interactive Streamlit dashboard, and Dockerized deployment assets.

## Improvements to take this further

1. Replace the baseline staffing proxy with actual scheduled roster data.
2. Move from district-watch planning to district-hour planning.
3. Add adjacency and travel-time constraints between districts or beats.
4. Introduce service-level constraints for priority 1 response performance.
5. Calibrate staffing benefit using observed response times.
6. Extend to robust or stochastic optimization using forecasted call scenarios.
7. Add beat-level geospatial boundaries for choropleth mapping.
