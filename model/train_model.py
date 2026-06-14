import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, accuracy_score

def train_models(data_path=None):
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "railways.parquet")

    df = pd.read_parquet(data_path)

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    le_station = LabelEncoder()
    all_stations = pd.concat([df["from_station"], df["to_station"]]).unique()
    le_station.fit(all_stations)
    df["from_encoded"] = le_station.transform(df["from_station"])
    df["to_encoded"] = le_station.transform(df["to_station"])

    le_weather = LabelEncoder()
    df["weather_encoded"] = le_weather.fit_transform(df["weather"])

    le_train = LabelEncoder()
    df["train_encoded"] = le_train.fit_transform(df["train_name"])

    features = [
        "distance_km", "hour_sin", "hour_cos", "dow_sin", "dow_cos",
        "month_sin", "month_cos", "is_peak_hour", "from_encoded", "to_encoded",
        "weather_encoded", "train_encoded", "congestion_index"
    ]

    X = df[features]
    y_reg = df["delay_minutes"]
    y_clf = (df["delay_minutes"] > 15).astype(int)

    X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
        X, y_reg, y_clf, test_size=0.2, random_state=42
    )

    reg_model = RandomForestRegressor(
        n_estimators=80, max_depth=12, random_state=42, n_jobs=-1
    )
    reg_model.fit(X_train, y_reg_train)
    reg_preds = reg_model.predict(X_test)
    reg_mae = mean_absolute_error(y_reg_test, reg_preds)

    clf_model = RandomForestClassifier(
        n_estimators=80, max_depth=10, random_state=42, n_jobs=-1
    )
    clf_model.fit(X_train, y_clf_train)
    clf_preds = clf_model.predict(X_test)
    clf_acc = accuracy_score(y_clf_test, clf_preds)

    model_dir = os.path.dirname(__file__)
    joblib.dump(reg_model, os.path.join(model_dir, "delay_regressor.pkl"), compress=3)
    joblib.dump(clf_model, os.path.join(model_dir, "delay_classifier.pkl"), compress=3)
    joblib.dump(le_station, os.path.join(model_dir, "station_encoder.pkl"))
    joblib.dump(le_weather, os.path.join(model_dir, "weather_encoder.pkl"))
    joblib.dump(le_train, os.path.join(model_dir, "train_encoder.pkl"))
    joblib.dump(features, os.path.join(model_dir, "feature_columns.pkl"))

    print(f"[REG] Delay Prediction MAE: {reg_mae:.2f} minutes")
    print(f"[CLF] Delay Classification Accuracy: {clf_acc:.2%}")
    print(f"Models saved to model/ (compressed)")

    return reg_model, clf_model

if __name__ == "__main__":
    train_models()
