from collections import Counter, defaultdict
from datetime import datetime


def extract_features(events: list[dict]) -> dict:
    """
    Extract numerical features from structured log events.
    """

    total_events = len(events)

    if total_events == 0:
        return {
            "total_events": 0,
            "info_count": 0,
            "warning_count": 0,
            "error_count": 0,
            "critical_count": 0,
            "error_rate": 0.0,
            "category_counts": {},
            "events_per_minute": {}
        }

    # Count log levels
    level_counts = Counter(
        event.get("level", "UNKNOWN").upper()
        for event in events
    )

    # Count categories
    category_counts = Counter(
        event.get("category", "UNKNOWN")
        for event in events
    )

    # Calculate error rate
    error_count = level_counts.get("ERROR", 0)
    critical_count = level_counts.get("CRITICAL", 0)

    error_rate = (
        (error_count + critical_count) / total_events
    ) * 100

    # Count events per minute
    events_per_minute = defaultdict(int)

    for event in events:
        timestamp = datetime.fromisoformat(event["timestamp"])
        minute_key = timestamp.strftime("%Y-%m-%d %H:%M")
        events_per_minute[minute_key] += 1

    return {
        "total_events": total_events,
        "info_count": level_counts.get("INFO", 0),
        "warning_count": level_counts.get("WARNING", 0),
        "error_count": error_count,
        "critical_count": critical_count,
        "error_rate": round(error_rate, 2),
        "category_counts": dict(category_counts),
        "events_per_minute": dict(events_per_minute)
    }
