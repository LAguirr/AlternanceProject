from ..core.celery_app import celery_app
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

STORAGE_DIR = os.getenv('STORAGE_DIR', '/code/models_storage')

@celery_app.task(bind=True)
def train_model_task(self, dataset_path: str, target_column: str, model_type: str, model_name: str=None):
    df = pd.read_csv(dataset_path)
    if target_column not in df.columns:
        return {'status': 'error', 'msg': 'target not in columns'}

    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Quick preprocessing: drop non-numeric cols (MVP); expand later
    X = X.select_dtypes(include=['number']).fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'xgboost':
        model = XGBRegressor()
    else:
        # Placeholder for simple NN or other
        model = LinearRegression()

    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)

    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    model_filename = model_name or f"model_{int(pd.Timestamp.now().timestamp())}.joblib"
    model_path = os.path.join(STORAGE_DIR, model_filename)
    joblib.dump({'model': model, 'columns': X.columns.tolist()}, model_path)

    return {'status': 'ok', 'model_path': model_path, 'mse': float(mse)}