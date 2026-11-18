
from backend.services.ai_agent import diagnose_incident


sample_incident = {
    "incident_id": "INC-TEST-001",
    "title": "Database Error Incident",
    "severity": "CRITICAL",
    "primary_category": "DATABASE_ERROR",
    "first_seen": "2026-11-17T10:00:10",
    "last_seen": "2026-11-17T10:00:20",
    "event_count": 3,
    "correlation_reason": "Three related events detected within 10 seconds.",
    "events": [
        {
            "timestamp": "2026-11-17T10:00:10",
            "level": "ERROR",
            "category": "DATABASE_ERROR",
            "severity": "HIGH",
            "message": "Database connection failed"
        },
        {
            "timestamp": "2026-11-17T10:00:15",
            "level": "ERROR",
            "category": "DATABASE_ERROR",
            "severity": "HIGH",
            "message": "Connection timeout while accessing MySQL"
        },
        {
            "timestamp": "2026-11-17T10:00:20",
            "level": "CRITICAL",
            "category": "SYSTEM_ERROR",
            "severity": "CRITICAL",
            "message": "Application service unavailable"
        }
    ]
}


if __name__ == "__main__":
    print("\n========== LOGMIND AI - AI DIAGNOSIS ==========\n")

    try:
        diagnosis = diagnose_incident(sample_incident)

        print("SUMMARY:")
        print(diagnosis["summary"])

        print("\nROOT CAUSES:")
        for cause in diagnosis["root_causes"]:
            print("\nHypothesis:", cause["hypothesis"])
            print("Evidence:", cause["evidence"])
            print("Confidence:", cause["confidence"])

        print("\nRECOMMENDATIONS:")
        for recommendation in diagnosis["recommendations"]:
            print("-", recommendation)

        print("\nLIMITATIONS:")
        for limitation in diagnosis["limitations"]:
            print("-", limitation)

        print("\nAI DIAGNOSIS COMPLETED SUCCESSFULLY!")

    except Exception as error:
        print("\nAI DIAGNOSIS FAILED:", error)
