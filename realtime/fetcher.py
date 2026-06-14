import logging
from datetime import datetime, timedelta

from ntes import NTESClient
from ntes.exceptions import NTESError
from utils.simulation import RailSimulator
from .distance_lookup import lookup_distance

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("RailwayFetcher")

STALE_AFTER = timedelta(seconds=120)

def _parse_delay(delay_str):
    if not delay_str or delay_str in ("RT", "On Time", "On time", ""):
        return 0
    try:
        delay_str = delay_str.replace("late by", "").replace("min", "").strip()
        return int(delay_str)
    except (ValueError, AttributeError):
        return 0

class RailwayFetcher:
    def __init__(self):
        self._ntes = NTESClient(timeout=10)
        self._sim = RailSimulator()
        self._cache = None
        self._cache_time = None
        self._last_error = None

    @property
    def is_live(self):
        return self._cache_time is not None and (datetime.now() - self._cache_time) < STALE_AFTER

    @property
    def last_updated(self):
        return self._cache_time

    @property
    def last_error(self):
        return self._last_error

    def _fetch_ntes(self):
        try:
            data = self._ntes.station_live("NGP")
            trains = data.get("TrainsAtStation", [])
            if trains:
                return trains
        except Exception as e:
            log.warning(f"NTES NGP: {e}")
        return None

    def _parse_train(self, raw):
        raw_name = raw.get("TrainName", "Unknown Express")

        source = raw.get("SourceName", "")
        if not source:
            source_code = raw.get("STA", "")
            source = source_code

        dest = raw.get("DestinationName", "")
        if not dest:
            dest_code = raw.get("Destination", "")
            dest = dest_code

        std_raw = raw.get("STD", "")
        dep_time = None
        if std_raw:
            try:
                dep_time = datetime.strptime(std_raw, "%H:%M %d-%b")
                dep_time = dep_time.replace(year=datetime.now().year)
            except ValueError:
                try:
                    dep_time = datetime.strptime(std_raw.split()[0], "%H:%M")
                    dep_time = dep_time.replace(
                        year=datetime.now().year,
                        month=datetime.now().month,
                        day=datetime.now().day,
                    )
                except ValueError:
                    dep_time = datetime.now()

        delay_arr = raw.get("DelayArr", "RT")
        delay_dep = raw.get("DelayDep", delay_arr)
        delay_val = max(_parse_delay(delay_arr), _parse_delay(delay_dep))

        is_cancelled = raw.get("Cancel", "0") in ("1", "True", True)

        if is_cancelled:
            status = "cancelled"
        elif delay_val > 15:
            status = "delayed"
        else:
            status = "on_time"

        train_id = raw.get("TrainNumber", raw.get("TrainNo", str(raw.get("TrainName", ""))))
        platform = raw.get("Platform", "")

        dist = lookup_distance(source, dest)
        if dist is None:
            dist = lookup_distance(dest, source)

        return {
            "train_id": str(train_id),
            "train_name": raw_name,
            "from_station": source,
            "to_station": dest,
            "platform": platform,
            "distance_km": dist or 0,
            "scheduled_departure": dep_time or datetime.now(),
            "delay_minutes": delay_val,
            "simulated_delay": delay_val,
            "status": status,
            "weather": "clear",
            "current_time": datetime.now(),
        }

    def get_live_trains(self, n=15):
        raw_trains = self._fetch_ntes()

        if raw_trains:
            parsed = [self._parse_train(t) for t in raw_trains[:n]]
            self._cache = parsed
            self._cache_time = datetime.now()
            self._last_error = None
            log.info(f"Fetched {len(parsed)} trains from NTES")
            return parsed

        self._last_error = "NTES unavailable, using fallback"
        log.info("Fallback to simulation")
        self._cache = None
        return self._sim.get_live_trains(n)

    def current_stats(self):
        if self._cache:
            delays = [t["delay_minutes"] for t in self._cache]
            statuses = [t["status"] for t in self._cache]
            total = len(self._cache)
            on_time = sum(1 for s in statuses if s == "on_time")
            delayed = sum(1 for s in statuses if s == "delayed")
            return {
                "on_time_pct": round(on_time / total * 100, 1),
                "delayed_pct": round(delayed / total * 100, 1),
                "avg_delay": round(sum(delays) / total, 1) if total else 0,
                "active_trains": total,
            }
        return {"on_time_pct": 0, "delayed_pct": 0, "avg_delay": 0, "active_trains": 0}

    def status_text(self):
        if self.is_live:
            return "🔴 LIVE"
        return "🟡 FALLBACK"
