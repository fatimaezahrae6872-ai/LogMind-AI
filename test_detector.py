import unittest

from backend.services.detector import (
    classify_category,
    classify_severity,
    detect_event,
    detect_events
)


class TestDetectionEngine(unittest.TestCase):

    def test_database_detection(self):
        category, reason = classify_category(
            "Database connection failed"
        )
        self.assertEqual(category, "DATABASE_ERROR")
        self.assertIn("database", reason)

    def test_network_detection(self):
        category, _ = classify_category(
            "Connection refused"
        )
        self.assertEqual(category, "NETWORK_ERROR")

    def test_performance_detection(self):
        category, _ = classify_category(
            "High response time detected"
        )
        self.assertEqual(category, "PERFORMANCE_ISSUE")

    def test_unknown_detection(self):
        category, _ = classify_category(
            "User logged in successfully"
        )
        self.assertEqual(category, "UNKNOWN")

    def test_severity(self):
        self.assertEqual(classify_severity("ERROR"), "HIGH")
        self.assertEqual(classify_severity("CRITICAL"), "CRITICAL")
        self.assertEqual(classify_severity("INFO"), "LOW")

    def test_detect_event(self):
        event = {
            "level": "ERROR",
            "message": "Database connection failed",
            "is_parsed": True
        }

        result = detect_event(event)

        self.assertEqual(result["category"], "DATABASE_ERROR")
        self.assertEqual(result["severity"], "HIGH")
        self.assertIn("detection_reason", result)

    def test_detect_multiple_events(self):
        events = [
            {
                "level": "ERROR",
                "message": "Database connection failed"
            },
            {
                "level": "WARNING",
                "message": "High response time detected"
            }
        ]

        results = detect_events(events)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["category"], "DATABASE_ERROR")
        self.assertEqual(results[1]["category"], "PERFORMANCE_ISSUE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
