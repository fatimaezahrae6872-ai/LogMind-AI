import unittest

from backend.services.feature_extractor import extract_features


class TestFeatureExtractor(unittest.TestCase):

    def setUp(self):
        self.events = [
            {
                "timestamp": "2026-11-16 10:00:01",
                "level": "INFO",
                "category": "UNKNOWN"
            },
            {
                "timestamp": "2026-11-16 10:00:10",
                "level": "WARNING",
                "category": "PERFORMANCE_ISSUE"
            },
            {
                "timestamp": "2026-11-16 10:00:15",
                "level": "ERROR",
                "category": "DATABASE_ERROR"
            },
            {
                "timestamp": "2026-11-16 10:00:16",
                "level": "ERROR",
                "category": "APPLICATION_ERROR"
            },
            {
                "timestamp": "2026-11-16 10:00:20",
                "level": "CRITICAL",
                "category": "SYSTEM_ERROR"
            }
        ]

    def test_total_events(self):
        features = extract_features(self.events)
        self.assertEqual(features["total_events"], 5)

    def test_level_counts(self):
        features = extract_features(self.events)

        self.assertEqual(features["info_count"], 1)
        self.assertEqual(features["warning_count"], 1)
        self.assertEqual(features["error_count"], 2)
        self.assertEqual(features["critical_count"], 1)

    def test_error_rate(self):
        features = extract_features(self.events)
        self.assertEqual(features["error_rate"], 60.0)

    def test_category_counts(self):
        features = extract_features(self.events)

        self.assertEqual(
            features["category_counts"]["DATABASE_ERROR"],
            1
        )

    def test_events_per_minute(self):
        features = extract_features(self.events)

        self.assertEqual(
            features["events_per_minute"]["2026-11-16 10:00"],
            5
        )

    def test_empty_events(self):
        features = extract_features([])

        self.assertEqual(features["total_events"], 0)
        self.assertEqual(features["error_rate"], 0.0)
        self.assertEqual(features["events_per_minute"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
