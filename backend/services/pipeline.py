from collections import Counter

from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines
from backend.services.detector import detect_events
from backend.services.correlator import correlate_events


def analyze_log_file(file_path: str) -> dict:

    # STEP 1: Ingestion
    file_info = ingest_log_file(file_path)

    # STEP 2: Parsing
    parsed_events = parse_log_lines(file_info.content)

    # STEP 3: Detection
    detected_events = detect_events(parsed_events)

    # STEP 4: Incident Correlation
    # Les événements sans timestamp ne peuvent pas être corrélés.
    timestamped_events = [
        event for event in detected_events
        if event.get("timestamp") is not None
    ]

    incidents = correlate_events(timestamped_events)

    # STEP 5: Statistics
    category_counts = dict(
        Counter(event["category"] for event in detected_events)
    )

    severity_counts = dict(
        Counter(event["severity"] for event in detected_events)
    )

    successful_parsing = sum(
        event["is_parsed"] for event in parsed_events
    )

    parsing_rate = (
        successful_parsing / len(parsed_events) * 100
        if parsed_events else 0
    )

    return {
        "file": {
            "filename": file_info.filename,
            "size_bytes": file_info.size_bytes,
            "total_lines": file_info.total_lines,
            "empty_lines": file_info.empty_lines
        },
        "summary": {
            "parsed_events": len(parsed_events),
            "successful_parsing": successful_parsing,
            "parsing_rate": round(parsing_rate, 2),
            "detected_events": len(detected_events),
            "incident_count": len(incidents)
        },
        "statistics": {
            "categories": category_counts,
            "severities": severity_counts
        },
        "events": detected_events,
        "incidents": incidents
    }
