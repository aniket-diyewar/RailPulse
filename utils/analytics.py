import pandas as pd
import numpy as np

def load_data():
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "data", "railways.parquet")
    return pd.read_parquet(path)

def station_stats(df):
    delay_by_station = df.groupby("from_station")["delay_minutes"].agg(["mean", "max", "count"]).round(1)
    delay_by_station.columns = ["avg_delay", "max_delay", "train_count"]
    return delay_by_station.sort_values("avg_delay", ascending=False)

def peak_hour_analysis(df):
    return df.groupby("is_peak_hour").agg(
        avg_delay=("delay_minutes", "mean"),
        max_delay=("delay_minutes", "max"),
        delay_rate=("delay_minutes", lambda x: (x > 15).mean())
    ).round(2)

def weather_impact(df):
    return df.groupby("weather").agg(
        avg_delay=("delay_minutes", "mean"),
        count=("delay_minutes", "count"),
        delay_rate=("delay_minutes", lambda x: (x > 15).mean())
    ).round(2)

def hourly_pattern(df):
    return df.groupby("hour").agg(
        avg_delay=("delay_minutes", "mean"),
        volume=("train_id", "count")
    ).round(2)

def on_time_rate(df):
    return (df["status"] == "on_time").mean()

def top_routes(df):
    route_delays = df.groupby(["from_station", "to_station"]).agg(
        avg_delay=("delay_minutes", "mean"),
        total_trains=("train_id", "count")
    ).round(1).sort_values("avg_delay", ascending=False).head(10)
    return route_delays

def monthly_trend(df):
    return df.groupby("month").agg(
        avg_delay=("delay_minutes", "mean"),
        total=("train_id", "count"),
        delay_rate=("delay_minutes", lambda x: (x > 15).mean())
    ).round(2)

def delay_distribution(df, bins=20):
    delays = df["delay_minutes"].values
    counts, edges = np.histogram(delays, bins=bins)
    return pd.DataFrame({"min": edges[:-1], "max": edges[1:], "count": counts})

def overall_summary(df):
    ss = station_stats(df)
    return {
        "total_trains": len(df),
        "on_time_pct": round((df["status"] == "on_time").mean() * 100, 1),
        "delayed_pct": round((df["status"] == "delayed").mean() * 100, 1),
        "cancelled_pct": round((df["status"] == "cancelled").mean() * 100, 1),
        "avg_delay": round(df["delay_minutes"].mean(), 1),
        "max_delay": round(df["delay_minutes"].max(), 1),
        "busiest_station": df["from_station"].mode()[0],
        "worst_station": ss.index[0] if len(ss) > 0 else "N/A",
    }
