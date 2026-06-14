import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

STATIONS = [
    "New Delhi", "Mumbai Central", "Howrah", "Chennai Central", "Bengaluru City",
    "Secunderabad", "Ahmedabad", "Jaipur", "Lucknow", "Patna",
    "Bhopal", "Chandigarh", "Pune", "Kolkata", "Thiruvananthapuram",
    "Guwahati", "Bhubaneswar", "Jodhpur", "Varanasi", "Nagpur",
    "Agra", "Surat", "Indore", "Coimbatore", "Madurai",
    "Visakhapatnam", "Ranchi", "Dehradun", "Amritsar", "Mysuru",
]

ROUTES = [
    ("New Delhi", "Mumbai Central", 1384), ("New Delhi", "Howrah", 1450),
    ("Mumbai Central", "Chennai Central", 1200), ("Howrah", "Chennai Central", 1660),
    ("New Delhi", "Bengaluru City", 2100), ("Mumbai Central", "Bengaluru City", 980),
    ("New Delhi", "Lucknow", 550), ("New Delhi", "Jaipur", 300),
    ("Mumbai Central", "Ahmedabad", 520), ("Howrah", "Patna", 530),
    ("Chennai Central", "Bengaluru City", 350), ("New Delhi", "Chandigarh", 260),
    ("Mumbai Central", "Pune", 180), ("Howrah", "Guwahati", 1010),
    ("New Delhi", "Varanasi", 820), ("Bengaluru City", "Thiruvananthapuram", 720),
    ("Mumbai Central", "Bhopal", 780), ("New Delhi", "Nagpur", 1090),
    ("Howrah", "Bhubaneswar", 440), ("Jaipur", "Jodhpur", 330),
    ("Nagpur", "Mumbai Central", 800), ("Nagpur", "Secunderabad", 500),
    ("Nagpur", "Bhopal", 300), ("Nagpur", "Chennai Central", 1100),
    ("New Delhi", "Agra", 220), ("Mumbai Central", "Surat", 260),
    ("Indore", "Bhopal", 190), ("Chennai Central", "Coimbatore", 500),
    ("Chennai Central", "Madurai", 460), ("Howrah", "Ranchi", 420),
    ("Visakhapatnam", "Howrah", 880), ("New Delhi", "Dehradun", 310),
    ("New Delhi", "Amritsar", 450), ("Bengaluru City", "Mysuru", 140),
    ("Pune", "Secunderabad", 560), ("Ahmedabad", "Surat", 230),
    ("Jaipur", "Agra", 240), ("Lucknow", "Varanasi", 280),
    ("Secunderabad", "Chennai Central", 650), ("New Delhi", "Indore", 800),
    ("Mumbai Central", "Indore", 590), ("Howrah", "Visakhapatnam", 880),
    ("Chennai Central", "Mysuru", 500), ("Secunderabad", "Bengaluru City", 610),
    ("Pune", "Mumbai Central", 180), ("Kolkata", "Howrah", 10),
]

TRAIN_NAMES = sorted([
    "Rajdhani Express", "Shatabdi Express", "Duronto Express", "Garib Rath",
    "Sampark Kranti", "Humsafar Express", "Tejas Express", "Vande Bharat",
    "Jan Shatabdi", "Superfast Express", "Mail Express", "Intercity Express",
    "Uday Express", "Antyodaya Express", "Mahamana Express", "Kavi Guru Express",
    "Vivek Express", "Shram Shakti Express", "Gatimaan Express", "Double Decker",
    "Jan Sadharan Express", "Yuva Express", "Rajya Rani Express", "Mahananda Express",
    "Gitanjali Express", "Shatabdi (Women)", "Hirakhand Express", "Konark Express",
    "Matsyagandha Express", "Netravati Express",
])

TRAIN_CLASSES = [
    ("Sleeper", 0.30), ("AC 3-Tier", 0.25), ("AC 2-Tier", 0.15),
    ("AC 1st Class", 0.05), ("General", 0.10), ("Chair Car", 0.10),
    ("Executive CC", 0.05),
]

BASE_FARES = {
    "Sleeper": lambda km: int(km * 0.8 + 50),
    "AC 3-Tier": lambda km: int(km * 2.0 + 100),
    "AC 2-Tier": lambda km: int(km * 3.0 + 150),
    "AC 1st Class": lambda km: int(km * 5.0 + 300),
    "General": lambda km: int(km * 0.5 + 30),
    "Chair Car": lambda km: int(km * 2.5 + 120),
    "Executive CC": lambda km: int(km * 4.5 + 250),
}

def random_date(start, end):
    return start + timedelta(seconds=np.random.randint(0, int((end - start).total_seconds())))

def generate_weather():
    w = np.random.choice(["clear", "rain", "fog", "storm"], p=[0.50, 0.28, 0.15, 0.07])
    mult = {"clear": 0, "rain": 0.15, "fog": 0.25, "storm": 0.40}
    return w, mult[w]

def generate_dataset(num_records=100000):
    rows = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 12, 31)
    class_names = [c[0] for c in TRAIN_CLASSES]
    class_probs = [c[1] for c in TRAIN_CLASSES]

    for _ in range(num_records):
        from_st, to_st, dist = ROUTES[np.random.randint(0, len(ROUTES))]
        if np.random.random() < 0.5:
            from_st, to_st = to_st, from_st
        tname = np.random.choice(TRAIN_NAMES)
        tid = f"{np.random.randint(10001, 99999)}"
        train_class = np.random.choice(class_names, p=class_probs)
        platform = np.random.randint(1, 12)

        sched_dep = random_date(start_date, end_date)
        travel_hrs = dist / np.random.uniform(50, 90)
        sched_arr = sched_dep + timedelta(hours=travel_hrs)

        hour = sched_dep.hour
        month = sched_dep.month
        dow = sched_dep.weekday()
        is_weekend = 1 if dow >= 5 else 0
        peak = 1 if (7 <= hour <= 10) or (16 <= hour <= 20) else 0

        weather, wmult = generate_weather()
        congestion = np.random.uniform(0.5, 1.8)

        # Monsoon boost (Jun-Sep)
        monsoon_boost = 0.15 if 6 <= month <= 9 else 0
        # Festival boost (Oct-Dec)
        festival_boost = 0.10 if 10 <= month <= 12 else 0
        # Weekend effect
        weekend_boost = 0.05 if is_weekend else 0

        base_delay = 0
        base_delay += peak * np.random.exponential(7)
        base_delay += wmult * np.random.exponential(25)
        base_delay += max(0, (congestion - 0.8) * 12)
        base_delay += monsoon_boost * np.random.exponential(20)
        base_delay += festival_boost * np.random.exponential(15)
        base_delay += weekend_boost * np.random.exponential(10)
        base_delay += np.random.exponential(4)

        base_delay = max(0, base_delay)
        delay_minutes = round(base_delay, 1)

        status = "on_time"
        if delay_minutes > 15:
            status = np.random.choice(["delayed", "on_time"], p=[0.65, 0.35])
        if delay_minutes > 60:
            status = np.random.choice(["delayed", "cancelled"], p=[0.82, 0.18])
        if delay_minutes <= 15:
            status = "on_time"
            delay_minutes = round(np.random.exponential(3), 1)

        actual_arr = sched_arr + timedelta(minutes=delay_minutes)
        fare = BASE_FARES[train_class](dist)
        occupancy = round(np.random.uniform(0.4, 1.0), 2)

        rows.append({
            "train_id": tid,
            "train_name": tname,
            "from_station": from_st,
            "to_station": to_st,
            "distance_km": dist,
            "train_class": train_class,
            "platform": platform,
            "ticket_price": fare,
            "occupancy_pct": occupancy,
            "scheduled_departure": sched_dep,
            "scheduled_arrival": sched_arr,
            "actual_arrival": actual_arr,
            "delay_minutes": delay_minutes,
            "status": status,
            "hour": hour,
            "is_peak_hour": peak,
            "is_weekend": is_weekend,
            "weather": weather,
            "congestion_index": round(congestion, 2),
            "day_of_week": dow,
            "month": month,
        })

    df = pd.DataFrame(rows)
    out = os.path.dirname(__file__)
    df.to_parquet(os.path.join(out, "railways.parquet"), index=False)
    df.to_csv(os.path.join(out, "railways.csv"), index=False)
    print(f"Generated {len(df):,} records -> data/railways.parquet")
    print(f"Columns: {list(df.columns)}")
    print(f"Status distribution:\n{df['status'].value_counts(normalize=True).to_string()}")
    print(f"Avg delay: {df['delay_minutes'].mean():.1f} min")
    print(f"Stations: {df['from_station'].nunique()}, Routes: {df.groupby(['from_station','to_station']).ngroups}")
    return df

if __name__ == "__main__":
    generate_dataset()
