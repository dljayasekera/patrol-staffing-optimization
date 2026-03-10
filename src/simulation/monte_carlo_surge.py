
import pandas as pd
import numpy as np

def simulate(input_csv, out_csv, sims=500):
    df = pd.read_csv(input_csv)
    results = []

    for s in range(sims):
        surge = np.random.lognormal(mean=0,sigma=0.3,len(df))
        sim_calls = df["calls"] * surge
        unmet = np.maximum(sim_calls - df["calls"],0)

        results.append({
            "sim": s,
            "total_calls": sim_calls.sum(),
            "unmet": unmet.sum()
        })

    pd.DataFrame(results).to_csv(out_csv,index=False)
    print("Saved simulation:", out_csv)

if __name__ == "__main__":
    import sys
    simulate(sys.argv[1], sys.argv[2])
