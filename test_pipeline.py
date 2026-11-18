from backend.services.pipeline import analyze_log_file


result = analyze_log_file(
    "data/samples/application.log"
)

print("\n========== LOGMIND AI - FULL PIPELINE ==========")

print("\nFILE INFORMATION")
print(result["file"])

print("\nANALYSIS SUMMARY")
for key, value in result["summary"].items():
    print(f"{key}: {value}")

print("\nCATEGORY STATISTICS")
for category, count in result["statistics"]["categories"].items():
    print(f"{category}: {count}")

print("\nSEVERITY STATISTICS")
for severity, count in result["statistics"]["severities"].items():
    print(f"{severity}: {count}")

print("\nINCIDENTS")

for incident in result["incidents"]:
    print(f"\nIncident ID: {incident['incident_id']}")
    print(f"Title: {incident['title']}")
    print(f"Severity: {incident['severity']}")
    print(f"Category: {incident['primary_category']}")
    print(f"Events: {incident['event_count']}")
    print(f"Triggers: {incident['trigger_count']}")
    print(f"First seen: {incident['first_seen']}")
    print(f"Last seen: {incident['last_seen']}")
    print(f"Reason: {incident['correlation_reason']}")

print("\nFULL PIPELINE COMPLETED!")
