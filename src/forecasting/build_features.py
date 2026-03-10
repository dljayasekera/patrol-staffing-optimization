
import pandas as pd

def build_features(input_file, out_file):
    df = pd.read_excel(input_file)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df["hour"] = df["date"].dt.hour
        df["dayofweek"] = df["date"].dt.dayofweek
    df["calls"] = 1
    out = df.groupby(["district","hour","dayofweek"]).agg({"calls":"sum"}).reset_index()
    out.to_csv(out_file, index=False)
    print("Saved features:", out_file)

if __name__ == "__main__":
    import sys
    build_features(sys.argv[1], sys.argv[2])
