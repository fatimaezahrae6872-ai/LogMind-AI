from collections import Counter

from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines
from backend.services.detector import detect_events


# 1. Ingestion
file_info = ingest_log_file("data/samples/application.log")

# 2. Parsing
parsed_events = parse_log_lines(file_info.content)

# 3. Detection
detected_events = detect_events(parsed_events)


print("\n========== LOGMIND AI - DETECTION ENGINE ==========")
print("File:", file_info.filename)
print("Raw lines:", file_info.total_lines)
print("Parsed events:", len(parsed_events))
print("Detected events:", len(detected_events))

print("\n========== DETECTED EVENTS ==========\n")

for event in detected_events:
    print(f"Line       : {event['line_number']}")
    print(f"Timestamp  : {event['timestamp']}")
    print(f"Level      : {event['level']}")
    print(f"Category   : {event['category']}")
    print(f"Severity   : {event['severity']}")
    print(f"Message    : {event['message']}")
    print(f"Reason     : {event['detection_reason']}")
    print("-" * 55)


print("\n========== STATISTICS ==========")

category_counts = Counter(
    event["category"] for event in detected_events
)

severity_counts = Counter(
    event["severity"] for event in detected_events
)

print("\nCategories:")
for category, count in category_counts.items():
    print(f"{category}: {count}")

print("\nSeverities:")
for severity, count in severity_counts.items():
    print(f"{severity}: {count}")


assert len(parsed_events) == len(detected_events)

print("\nPipeline completed successfully!")
