import numpy as np
from datetime import datetime, timedelta

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

TRAIN_NAMES = [
    "Rajdhani Express", "Shatabdi Express", "Duronto Express", "Garib Rath",
    "Sampark Kranti", "Humsafar Express", "Tejas Express", "Vande Bharat",
    "Jan Shatabdi", "Superfast Express", "Mail Express", "Intercity Express",
    "Uday Express", "Antyodaya Express", "Mahamana Express", "Kavi Guru Express",
    "Vivek Express", "Shram Shakti Express", "Gatimaan Express", "Double Decker",
    "Jan Sadharan Express", "Yuva Express", "Rajya Rani Express", "Mahananda Express",
    "Gitanjali Express", "Shatabdi (Women)", "Hirakhand Express", "Konark Express",
    "Matsyagandha Express", "Netravati Express",
]

WEATHERS = ["clear", "rain", "fog", "storm"]

class RailSimulator:
    def __init__(self):
        self._rng = np.random.default_rng()
        self._call_count = 0

    def _now(self):
        return datetime.now().replace(microsecond=0)

    def _pick_route(self):
        return ROUTES[self._rng.integers(0, len(ROUTES))]

    def _gen_delay(self, hour, month, weather):
        peak = 1 if (7 <= hour <= 10) or (16 <= hour <= 20) else 0
        wmult = {"clear": 0, "rain": 0.15, "fog": 0.25, "storm": 0.40}.get(weather, 0)
        is_weekend = 1 if self._now().weekday() >= 5 else 0
        monsoon = 0.15 if 6 <= month <= 9 else 0
        festival = 0.10 if 10 <= month <= 12 else 0
        congestion = self._rng.uniform(0.5, 1.5)

        d = 0
        d += peak * self._rng.exponential(7)
        d += wmult * self._rng.exponential(25)
        d += max(0, (congestion - 0.8) * 12)
        d += monsoon * self._rng.exponential(20)
        d += festival * self._rng.exponential(15)
        d += is_weekend * self._rng.exponential(8)
        d += self._rng.exponential(4)
        return max(0, round(d, 1))

    def _gen_status(self, delay):
        if delay > 60:
            return self._rng.choice(["delayed", "cancelled"], p=[0.82, 0.18])
        if delay > 15:
            return self._rng.choice(["delayed", "on_time"], p=[0.65, 0.35])
        return "on_time"

    def _gen_record(self, base_time, idx_offset=0):
        from_st, to_st, dist = self._pick_route()
        if self._rng.random() < 0.5:
            from_st, to_st = to_st, from_st
        # Stagger departures across the day
        dep_hour = (base_time.hour + idx_offset) % 24
        dep_min = self._rng.integers(0, 59)
        sched_dep = base_time.replace(hour=dep_hour, minute=dep_min, second=0)

        travel_mins = int(dist / self._rng.uniform(50, 90) * 60)
        sched_arr = sched_dep + timedelta(minutes=travel_mins)

        weather = self._rng.choice(WEATHERS, p=[0.50, 0.28, 0.15, 0.07])
        delay = self._gen_delay(dep_hour, base_time.month, weather)
        status = self._gen_status(delay)

        return {
            "train_id": str(self._rng.integers(10001, 99999)),
            "train_name": self._rng.choice(TRAIN_NAMES),
            "from_station": from_st,
            "to_station": to_st,
            "distance_km": dist,
            "scheduled_departure": sched_dep,
            "delay_minutes": delay,
            "simulated_delay": delay,
            "status": status,
            "weather": weather,
            "current_time": self._now(),
        }

    def get_live_trains(self, n=15):
        now = self._now()
        base = now - timedelta(hours=n // 2)
        trains = [self._gen_record(base, i) for i in range(n)]
        return trains

    def current_stats(self):
        now = self._now()
        n = 200
        trains = self.get_live_trains(n)
        delays = [t["delay_minutes"] for t in trains]
        statuses = [t["status"] for t in trains]
        on_time = sum(1 for s in statuses if s == "on_time")
        delayed = sum(1 for s in statuses if s == "delayed")
        total = len(trains)
        return {
            "on_time_pct": round(on_time / total * 100, 1),
            "delayed_pct": round(delayed / total * 100, 1),
            "avg_delay": round(sum(delays) / total, 1) if total else 0,
            "active_trains": total,
        }
