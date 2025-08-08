import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_linear_regression(csv_path: str, target_col: str, model_save_path: str):
    df = pd.read_csv(csv_path)
    if target_col not in df.columns:
        raise ValueError("target column not found")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Simple handling: drop non-numeric, fillna
    X = X.select_dtypes(include=[np.number]).fillna(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    rmse = mean_squared_error(y_test, preds, squared=False)
    r2 = r2_score(y_test, preds)

    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model, model_save_path)

    return {"rmse": rmse, "r2": r2}
