
from backend.core.database import get_incident_with_events

incident = get_incident_with_events(1)

if incident is None:
    print("Incident not found in database.")
else:
    print("========== INCIDENT RETRIEVAL ==========")
    print("ID:", incident["id"])
    print("Code:", incident["incident_code"])
    print("Title:", incident["title"])
    print("Severity:", incident["severity"])
    print("Category:", incident["primary_category"])

    print("\nOriginal events:")
    for event in incident["events"]:
        print("-", event.get("message"))
