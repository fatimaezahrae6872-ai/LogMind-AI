from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines
from backend.services.detector import detect_events
from backend.services.dataset_builder import build_time_dataset


# 1. Ingestion
file_info = ingest_log_file("data/samples/application.log")

# 2. Parsing
parsed_events = parse_log_lines(file_info.content)

# 3. Detection
detected_events = detect_events(parsed_events)

# 4. Dataset construction
dataset = build_time_dataset(detected_events)


print("\n========== LOGMIND AI - ML DATASET ==========")

print("\nDataset:")
print(dataset.to_string())

print("\n========== DATASET INFORMATION ==========")
print("Number of windows:", len(dataset))
print("Number of features:", len(dataset.columns))
print("Total events:", int(dataset["total_events"].sum()))

print("\n========== FEATURE COLUMNS ==========")
for column in dataset.columns:
    print("-", column)

print("\nDataset successfully generated!")
