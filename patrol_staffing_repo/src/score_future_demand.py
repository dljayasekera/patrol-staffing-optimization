
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
import joblib

def train_model(input_csv, model_out):
    df = pd.read_csv(input_csv)
    X = df[["district","hour","dayofweek"]]
    y = df["calls"]

    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    model = XGBRegressor(n_estimators=200,max_depth=5,learning_rate=0.05)
    model.fit(X_train,y_train)

    preds = model.predict(X_test)
    print("MAE:", mean_absolute_error(y_test,preds))

    joblib.dump(model, model_out)
    print("Saved model:", model_out)

if __name__ == "__main__":
    import sys
    train_model(sys.argv[1], sys.argv[2])
