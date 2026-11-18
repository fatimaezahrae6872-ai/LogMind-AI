import random
import pandas as pd

from backend.services.dataset_builder import FEATURE_COLUMNS


def generate_synthetic_dataset(
    n_windows: int = 500,
    anomaly_ratio: float = 0.10,
    seed: int = 42
) -> pd.DataFrame:

    if n_windows <= 0:
        raise ValueError("n_windows must be greater than zero.")

    if not 0 <= anomaly_ratio <= 1:
        raise ValueError("anomaly_ratio must be between 0 and 1.")

    rng = random.Random(seed)

    start_time = pd.Timestamp("2026-11-16 08:00:00")
    records = []

    anomaly_count = round(n_windows * anomaly_ratio)

    # Select anomaly positions
    anomaly_positions = set(
        rng.sample(range(n_windows), anomaly_count)
    )

    for i in range(n_windows):

        timestamp = start_time + pd.Timedelta(minutes=i)

        if i in anomaly_positions:

            # Simulate different abnormal behaviors
            scenario = rng.choice([
                "DATABASE_SPIKE",
                "NETWORK_FAILURE",
                "APPLICATION_CRASH"
            ])

            if scenario == "DATABASE_SPIKE":
                info = rng.randint(5, 15)
                warning = rng.randint(3, 8)
                error = rng.randint(8, 20)
                critical = rng.randint(0, 3)

            elif scenario == "NETWORK_FAILURE":
                info = rng.randint(3, 12)
                warning = rng.randint(5, 12)
                error = rng.randint(10, 18)
                critical = rng.randint(1, 4)

            else:
                info = rng.randint(1, 8)
                warning = rng.randint(2, 8)
                error = rng.randint(8, 15)
                critical = rng.randint(3, 7)

            label = "anomaly"

        else:

            # Simulate normal system activity
            info = rng.randint(12, 25)
            warning = rng.randint(0, 3)
            error = rng.randint(0, 1)
            critical = 0

            label = "normal"

            scenario = "NORMAL"

        total = info + warning + error + critical

        error_rate = round(
            ((error + critical) / total) * 100,
            2
        ) if total > 0 else 0.0

        records.append({
            "timestamp": timestamp,
            "total_events": total,
            "info_count": info,
            "warning_count": warning,
            "error_count": error,
            "critical_count": critical,
            "error_rate": error_rate,
            "label": label,
            "scenario": scenario
        })

    dataset = pd.DataFrame(records)
    dataset = dataset.set_index("timestamp")

    return dataset


if __name__ == "__main__":

    dataset = generate_synthetic_dataset()

    print("\n========== SYNTHETIC DATASET ==========")
    print(dataset.head(10))

    print("\n========== DATASET INFORMATION ==========")
    print("Total windows:", len(dataset))
    print("Total features:", len(FEATURE_COLUMNS))

    print("\n========== LABEL DISTRIBUTION ==========")
    print(dataset["label"].value_counts())

    print("\n========== SCENARIO DISTRIBUTION ==========")
    print(dataset["scenario"].value_counts())

    print("\nDataset generated successfully!")
