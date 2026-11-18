import pandas as pd


FEATURE_COLUMNS = [
    "total_events",
    "info_count",
    "warning_count",
    "error_count",
    "critical_count",
    "error_rate"
]


def build_time_dataset(
    events: list[dict],
    window: str = "1min"
) -> pd.DataFrame:

    if not events:
        empty_index = pd.DatetimeIndex(
            [],
            name="timestamp"
        )
        return pd.DataFrame(
            columns=FEATURE_COLUMNS,
            index=empty_index
        )

    df = pd.DataFrame(events)

    required_columns = {"timestamp", "level"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp"]).copy()

    if df.empty:
        empty_index = pd.DatetimeIndex(
            [],
            name="timestamp"
        )
        return pd.DataFrame(
            columns=FEATURE_COLUMNS,
            index=empty_index
        )

    df["level"] = (
        df["level"]
        .fillna("UNKNOWN")
        .str.upper()
    )

    # Count all events per time window
    total = (
        df.set_index("timestamp")
        .resample(window)
        .size()
        .rename("total_events")
    )

    # Count each severity level per time window
    level_counts = (
        df.groupby([
            pd.Grouper(key="timestamp", freq=window),
            "level"
        ])
        .size()
        .unstack(fill_value=0)
    )

    result = pd.DataFrame(index=total.index)

    result["total_events"] = total

    for level, column in [
        ("INFO", "info_count"),
        ("WARNING", "warning_count"),
        ("ERROR", "error_count"),
        ("CRITICAL", "critical_count")
    ]:
        if level in level_counts.columns:
            result[column] = (
                level_counts[level]
                .reindex(result.index, fill_value=0)
            )
        else:
            result[column] = 0

    errors = (
        result["error_count"] +
        result["critical_count"]
    )

    result["error_rate"] = (
        errors / result["total_events"] * 100
    ).round(2)

    result.index.name = "timestamp"

    return result[FEATURE_COLUMNS]
