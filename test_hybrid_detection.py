from backend.services.synthetic_data import generate_synthetic_dataset
from backend.services.dataset_builder import FEATURE_COLUMNS
from backend.services.anomaly_detector import (
    train_anomaly_detector,
    predict_hybrid
)

import pandas as pd


# Generate training data
dataset = generate_synthetic_dataset()

X = dataset[FEATURE_COLUMNS]

model = train_anomaly_detector(
    X,
    contamination=0.10
)

# Test cases
cases = pd.DataFrame([
    {
        "total_events": 23,
        "info_count": 18,
        "warning_count": 2,
        "error_count": 3,
        "critical_count": 0,
        "error_rate": 13.04
    },
    {
        "total_events": 20,
        "info_count": 18,
        "warning_count": 1,
        "error_count": 0,
        "critical_count": 1,
        "error_rate": 5.0
    },
    {
        "total_events": 34,
        "info_count": 30,
        "warning_count": 3,
        "error_count": 1,
        "critical_count": 0,
        "error_rate": 2.94
    }
], index=[
    "Mild error increase",
    "Single critical event",
    "High volume, low errors"
])

results = predict_hybrid(model, cases)

print("\n========== HYBRID DETECTION ==========")

for name, row in results.iterrows():
    print(f"\nCase: {name}")
    print("ML prediction:", row["ml_prediction"])
    print("Critical rule:", row["critical_rule"])
    print("Final prediction:", row["final_prediction"])
    print("Anomaly score:", round(row["anomaly_score"], 4))

assert (
    results.loc["Single critical event", "final_prediction"]
    == "ANOMALY"
)

assert (
    results.loc["Single critical event", "critical_rule"]
    == True
)

print("\nHybrid detection tests passed!")
