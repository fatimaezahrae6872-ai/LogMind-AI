from pathlib import Path

from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines
from backend.services.detector import detect_events
from backend.services.correlator import correlate_events
from backend.services.feature_extractor import extract_features
from backend.services.dataset_builder import build_time_dataset
from backend.services.synthetic_data import generate_synthetic_dataset
from backend.services.anomaly_detector import (
    train_anomaly_detector,
    predict_hybrid
)


def create_baseline_model():
    """
    Train the Isolation Forest model using synthetic baseline data.
    Labels and scenario columns are never used for training.
    """

    training_data = generate_synthetic_dataset(
        n_windows=500,
        anomaly_ratio=0.10,
        seed=42
    )

    model = train_anomaly_detector(
        training_data,
        contamination=0.10,
        random_state=42
    )

    return model


def analyze_log_file(
    file_path: str,
    model=None,
    window: str = "1min"
) -> dict:
    """
    Execute the complete LogMind AI analysis pipeline.
    """

    # 1. Ingestion
    file_info = ingest_log_file(file_path)

    # 2. Parsing
    parsed_events = parse_log_lines(file_info.content)

    # 3. Detection and classification
    detected_events = detect_events(parsed_events)

    # 4. Incident correlation
    incidents = correlate_events(detected_events)

    # 5. Statistical feature extraction
    statistics = extract_features(detected_events)

    # 6. Build temporal dataset
    time_dataset = build_time_dataset(
        detected_events,
        window=window
    )

    # 7. Train or reuse the ML model
    if model is None:
        model = create_baseline_model()

    # 8. Hybrid anomaly detection
    if not time_dataset.empty:
        anomaly_results = predict_hybrid(
            model,
            time_dataset
        )

        anomaly_records = []

        for timestamp, row in anomaly_results.iterrows():
            anomaly_records.append({
                "timestamp": timestamp.isoformat(),
                "ml_prediction": row["ml_prediction"],
                "anomaly_score": round(
                    float(row["anomaly_score"]), 4
                ),
                "critical_rule": bool(row["critical_rule"]),
                "final_prediction": row["final_prediction"]
            })

    else:
        anomaly_records = []

    # 9. Final response
    return {
        "file": {
            "filename": file_info.filename,
            "extension": file_info.extension,
            "size_bytes": file_info.size_bytes,
            "total_lines": file_info.total_lines,
            "empty_lines": file_info.empty_lines
        },
        "summary": {
            "total_events": len(detected_events),
            "total_incidents": len(incidents),
            "anomaly_windows": sum(
                item["final_prediction"] == "ANOMALY"
                for item in anomaly_records
            )
        },
        "statistics": statistics,
        "events": detected_events,
        "incidents": incidents,
        "anomalies": anomaly_records
    }


if __name__ == "__main__":

    sample_path = Path("data/samples/application.log")

    result = analyze_log_file(str(sample_path))

    print("\n========== LOGMIND AI ANALYSIS ==========")

    print("\nFILE INFORMATION")
    print(result["file"])

    print("\nSUMMARY")
    print(result["summary"])

    print("\nSTATISTICS")
    print(result["statistics"])

    print("\nINCIDENTS")
    for incident in result["incidents"]:
        print(
            incident["incident_id"],
            incident["severity"],
            incident["title"]
        )

    print("\nANOMALY DETECTION")
    for anomaly in result["anomalies"]:
        print(anomaly)

    print("\nAnalysis pipeline completed successfully!")
