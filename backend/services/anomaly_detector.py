from sklearn.ensemble import IsolationForest

from backend.services.dataset_builder import FEATURE_COLUMNS


def train_anomaly_detector(
    dataset,
    contamination=0.10,
    random_state=42
):
    missing = set(FEATURE_COLUMNS) - set(dataset.columns)

    if missing:
        raise ValueError(
            f"Missing features: {sorted(missing)}"
        )

    if dataset.empty:
        raise ValueError("Cannot train on an empty dataset.")

    X = dataset[FEATURE_COLUMNS]

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1
    )

    model.fit(X)

    return model


def predict_anomalies(model, dataset):
    missing = set(FEATURE_COLUMNS) - set(dataset.columns)

    if missing:
        raise ValueError(
            f"Missing features: {sorted(missing)}"
        )

    return model.predict(dataset[FEATURE_COLUMNS])

def predict_hybrid(model, dataset):
    """
    Combine Isolation Forest predictions
    with a critical-event safety rule.
    """

    predictions = predict_anomalies(model, dataset)

    results = dataset.copy()

    results["ml_prediction"] = [
        "ANOMALY" if prediction == -1 else "NORMAL"
        for prediction in predictions
    ]

    # Higher score = more unusual
    results["anomaly_score"] = (
        -model.decision_function(dataset[FEATURE_COLUMNS])
    )

    # Safety rule: any critical event triggers review
    results["critical_rule"] = (
        results["critical_count"] > 0
    )

    results["final_prediction"] = results.apply(
        lambda row: (
            "ANOMALY"
            if row["ml_prediction"] == "ANOMALY"
            or row["critical_rule"]
            else "NORMAL"
        ),
        axis=1
    )

    return results

