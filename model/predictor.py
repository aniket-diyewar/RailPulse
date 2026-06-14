import numpy as np
import pandas as pd
import joblib
import os

class DelayPredictor:
    def __init__(self):
        model_dir = os.path.dirname(__file__)
        self.regressor = joblib.load(os.path.join(model_dir, "delay_regressor.pkl"))
        self.classifier = joblib.load(os.path.join(model_dir, "delay_classifier.pkl"))
        self.station_encoder = joblib.load(os.path.join(model_dir, "station_encoder.pkl"))
        self.weather_encoder = joblib.load(os.path.join(model_dir, "weather_encoder.pkl"))
        self.train_encoder = joblib.load(os.path.join(model_dir, "train_encoder.pkl"))
        self.features = joblib.load(os.path.join(model_dir, "feature_columns.pkl"))

    def predict(self, from_station, to_station, distance_km, hour, day_of_week, month,
                is_peak_hour, weather, train_name, congestion_index=1.0):
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        dow_sin = np.sin(2 * np.pi * day_of_week / 7)
        dow_cos = np.cos(2 * np.pi * day_of_week / 7)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)

        try:
            from_enc = self.station_encoder.transform([from_station])[0]
        except ValueError:
            from_enc = 0
        try:
            to_enc = self.station_encoder.transform([to_station])[0]
        except ValueError:
            to_enc = 0
        try:
            wea_enc = self.weather_encoder.transform([weather])[0]
        except ValueError:
            wea_enc = 0
        try:
            tr_enc = self.train_encoder.transform([train_name])[0]
        except ValueError:
            tr_enc = 0

        X = pd.DataFrame([[
            distance_km, hour_sin, hour_cos, dow_sin, dow_cos,
            month_sin, month_cos, int(is_peak_hour), from_enc, to_enc,
            wea_enc, tr_enc, congestion_index
        ]], columns=self.features)

        delay_pred = self.regressor.predict(X)[0]
        delay_class = self.classifier.predict(X)[0]

        return {
            "predicted_delay_minutes": round(float(delay_pred), 1),
            "will_be_delayed": bool(delay_class),
        }
