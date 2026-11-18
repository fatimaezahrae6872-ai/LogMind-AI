from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from backend.services.synthetic_data import generate_synthetic_dataset
from backend.services.dataset_builder import FEATURE_COLUMNS
from backend.services.anomaly_detector import (
    train_anomaly_detector,
    predict_anomalies
)


# 1. Generate dataset
dataset = generate_synthetic_dataset()

# 2. Separate features and reference labels
X = dataset[FEATURE_COLUMNS]
y = (dataset["label"] == "anomaly").astype(int)

# 3. Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 4. Train without labels
model = train_anomaly_detector(
    X_train,
    contamination=0.10
)

# 5. Predict
raw_predictions = predict_anomalies(model, X_test)

# Isolation Forest: -1 = anomaly, 1 = normal
y_pred = (raw_predictions == -1).astype(int)

# 6. Evaluation
print("\n========== ISOLATION FOREST ==========")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

print("\n========== EVALUATION ==========")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("Precision:", round(precision_score(y_test, y_pred, zero_division=0), 4))
print("Recall:", round(recall_score(y_test, y_pred, zero_division=0), 4))
print("F1-score:", round(f1_score(y_test, y_pred, zero_division=0), 4))

print("\n========== CONFUSION MATRIX ==========")
print(confusion_matrix(y_test, y_pred, labels=[0, 1]))

print("\n========== CLASSIFICATION REPORT ==========")
print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["Normal", "Anomaly"],
        zero_division=0
    )
)

print("\nModel training and evaluation completed!")
