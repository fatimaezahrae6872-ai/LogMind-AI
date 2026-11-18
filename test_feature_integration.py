from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines
from backend.services.detector import detect_events
from backend.services.feature_extractor import extract_features


# 1. Ingestion
file_info = ingest_log_file("data/samples/application.log")

# 2. Parsing
parsed_events = parse_log_lines(file_info.content)

# 3. Detection
detected_events = detect_events(parsed_events)

# 4. Feature Extraction
features = extract_features(detected_events)


print("\n========== LOGMIND AI - FEATURE EXTRACTION ==========")

print("\nFile:", file_info.filename)
print("Total events:", features["total_events"])

print("\n========== LOG LEVEL STATISTICS ==========")
print("INFO:", features["info_count"])
print("WARNING:", features["warning_count"])
print("ERROR:", features["error_count"])
print("CRITICAL:", features["critical_count"])

print("\nError rate:", features["error_rate"], "%")

print("\n========== CATEGORY STATISTICS ==========")
for category, count in features["category_counts"].items():
    print(f"{category}: {count}")

print("\n========== EVENTS PER MINUTE ==========")
for minute, count in features["events_per_minute"].items():
    print(f"{minute}: {count} events")

print("\nFeature extraction completed successfully!")
