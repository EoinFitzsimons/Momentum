from typing import List
import random
from .persistence_iface import Driver, Track, RaceResult


def simulate_race(drivers: List[Driver], track: Track, seed: int = 0) -> List[RaceResult]:
    rnd = random.Random(seed)
    results = []
    # simple deterministic-ish model: higher raw_speed -> lower time
    for d in drivers:
        # base_time proportional to track length; scale by inverse of raw_speed
        base = track.length_km * 60.0  # base minutes for 1 unit speed
        speed_factor = max(1.0, 100.0 / max(0.1, d.raw_speed))
        noise = rnd.uniform(-2.0, 2.0)
        time_seconds = (base * speed_factor + noise)  # minutes-ish; treat as seconds for simplicity
        results.append(RaceResult(driver_id=d.id, position=0, time_seconds=float(time_seconds)))
    # sort by time ascending -> better is smaller time
    results.sort(key=lambda r: r.time_seconds)
    # assign positions
    for idx, r in enumerate(results, start=1):
        r.position = idx
    return results
