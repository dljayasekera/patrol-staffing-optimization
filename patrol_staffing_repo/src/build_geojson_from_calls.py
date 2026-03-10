
import pandas as pd
import joblib

def score(input_csv, model_file, out_csv):
    df = pd.read_csv(input_csv)
    model = joblib.load(model_file)

    X = df[["district","hour","dayofweek"]]
    df["predicted_calls"] = model.predict(X)
    df.to_csv(out_csv, index=False)
    print("Saved forecast:", out_csv)

if __name__ == "__main__":
    import sys
    score(sys.argv[1], sys.argv[2], sys.argv[3])
