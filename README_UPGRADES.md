
# Patrol Staffing Upgrade Pack

Adds three major capabilities:

1. **AI Demand Forecasting**
   - XGBoost model predicting patrol call demand.

2. **GIS Coverage Analysis**
   - Converts patrol calls to GeoJSON and renders patrol maps.

3. **Monte Carlo Surge Simulation**
   - Stress-tests staffing plans under random demand spikes.

## Usage examples

Forecasting:
python src/forecasting/build_features.py Patrol_POC.xlsx demand.csv
python src/forecasting/train_xgboost.py demand.csv models/xgb.joblib

GIS:
python src/gis/build_geojson_from_calls.py Patrol_POC.xlsx patrol_zones.geojson

Simulation:
python src/simulation/monte_carlo_surge.py demand.csv simulation_results.csv
