import unittest

from backend.services.correlator import correlate_events


class TestIncidentCorrelation(unittest.TestCase):

    def setUp(self):
        self.events = [
            {
                "timestamp": "2026-11-16 10:00:10",
                "level": "WARNING",
                "category": "PERFORMANCE_ISSUE",
                "severity": "MEDIUM",
                "message": "High response time"
            },
            {
                "timestamp": "2026-11-16 10:00:15",
                "level": "ERROR",
                "category": "DATABASE_ERROR",
                "severity": "HIGH",
                "message": "Database connection failed"
            },
            {
                "timestamp": "2026-11-16 10:00:16",
                "level": "ERROR",
                "category": "APPLICATION_ERROR",
                "severity": "HIGH",
                "message": "HTTP 500 Internal Server Error"
            },
            {
                "timestamp": "2026-11-16 10:00:20",
                "level": "CRITICAL",
                "category": "SYSTEM_ERROR",
                "severity": "CRITICAL",
                "message": "Application crashed"
            }
        ]

    def test_group_related_events(self):
        incidents = correlate_events(self.events)

        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0]["trigger_count"], 3)

    def test_incident_severity(self):
        incidents = correlate_events(self.events)

        self.assertEqual(
            incidents[0]["severity"],
            "CRITICAL"
        )

    def test_warning_context(self):
        incidents = correlate_events(self.events)

        self.assertEqual(
            incidents[0]["event_count"],
            4
        )

    def test_separate_incidents(self):
        events = [
            {
                "timestamp": "2026-11-16 10:00:00",
                "severity": "HIGH",
                "category": "DATABASE_ERROR"
            },
            {
                "timestamp": "2026-11-16 10:10:00",
                "severity": "CRITICAL",
                "category": "SYSTEM_ERROR"
            }
        ]

        incidents = correlate_events(events)

        self.assertEqual(len(incidents), 2)

    def test_no_incidents(self):
        events = [
            {
                "timestamp": "2026-11-16 10:00:00",
                "severity": "LOW",
                "category": "UNKNOWN"
            }
        ]

        incidents = correlate_events(events)

        self.assertEqual(incidents, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
