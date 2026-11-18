import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

from backend.services.synthetic_data import generate_synthetic_dataset
from backend.services.dataset_builder import FEATURE_COLUMNS
from backend.services.anomaly_detector import (
    train_anomaly_detector,
    predict_anomalies
)


# 1. Generate and split the same dataset
dataset = generate_synthetic_dataset()

X = dataset[FEATURE_COLUMNS]
y = (dataset["label"] == "anomaly").astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 2. Compare contamination values
print("\n========== CONTAMINATION COMPARISON ==========")

for contamination in [0.05, 0.10, 0.15]:

    model = train_anomaly_detector(
        X_train,
        contamination=contamination
    )

    predictions = predict_anomalies(model, X_test)
    y_pred = (predictions == -1).astype(int)

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\nContamination: {contamination}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1-score:  {f1:.3f}")

# 3. Create borderline cases
borderline_cases = pd.DataFrame([
    {
        "total_events": 23,
        "info_count": 18,
        "warning_count": 2,
        "error_count": 3,
        "critical_count": 0,
        "error_rate": round(3 / 23 * 100, 2)
    },
    {
        "total_events": 22,
        "info_count": 16,
        "warning_count": 5,
        "error_count": 1,
        "critical_count": 0,
        "error_rate": round(1 / 22 * 100, 2)
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
        "error_rate": round(1 / 34 * 100, 2)
    }
], index=[
    "Mild error increase",
    "Warning increase",
    "Single critical event",
    "High volume, low errors"
])

print("\n========== BORDERLINE CASES ==========")

for contamination in [0.05, 0.10, 0.15]:

    model = train_anomaly_detector(
        X_train,
        contamination=contamination
    )

    predictions = predict_anomalies(model, borderline_cases)

    print(f"\nContamination: {contamination}")

    for name, prediction in zip(
        borderline_cases.index,
        predictions
    ):
        result = "ANOMALY" if prediction == -1 else "NORMAL"
        print(f"{name}: {result}")

print("\nRobustness tests completed!")
