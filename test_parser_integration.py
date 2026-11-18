from backend.services.ingestion import ingest_log_file
from backend.services.parser import parse_log_lines

file_info = ingest_log_file("data/samples/application.log")

parsed_logs = parse_log_lines(file_info.content)

print("\n========== LOGMIND AI PARSER ==========")
print("File:", file_info.filename)
print("Raw lines:", file_info.total_lines)
print("Parsed events:", len(parsed_logs))

print("\nStructured events:\n")

for event in parsed_logs:
    print(event)

if parsed_logs:
    successful = sum(
        event["is_parsed"] for event in parsed_logs
    )

    rate = successful / len(parsed_logs) * 100

    print(f"\nParsing success rate: {rate:.2f}%")
