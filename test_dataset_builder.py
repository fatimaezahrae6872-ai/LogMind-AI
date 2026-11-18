import unittest
import pandas as pd

from backend.services.dataset_builder import build_time_dataset


class TestDatasetBuilder(unittest.TestCase):

    def setUp(self):
        self.events = [
            {
                "timestamp": "2026-11-16 10:00:01",
                "level": "INFO"
            },
            {
                "timestamp": "2026-11-16 10:00:10",
                "level": "WARNING"
            },
            {
                "timestamp": "2026-11-16 10:00:15",
                "level": "ERROR"
            },
            {
                "timestamp": "2026-11-16 10:00:16",
                "level": "ERROR"
            },
            {
                "timestamp": "2026-11-16 10:00:20",
                "level": "CRITICAL"
            },
            {
                "timestamp": "2026-11-16 10:01:05",
                "level": "INFO"
            }
        ]

    def test_dataset_type(self):
        result = build_time_dataset(self.events)
        self.assertIsInstance(result, pd.DataFrame)

    def test_number_of_windows(self):
        result = build_time_dataset(self.events)
        self.assertEqual(len(result), 2)

    def test_first_window_total(self):
        result = build_time_dataset(self.events)
        self.assertEqual(result.iloc[0]["total_events"], 5)

    def test_first_window_error_count(self):
        result = build_time_dataset(self.events)
        self.assertEqual(result.iloc[0]["error_count"], 2)
        self.assertEqual(result.iloc[0]["critical_count"], 1)

    def test_error_rate(self):
        result = build_time_dataset(self.events)
        self.assertEqual(result.iloc[0]["error_rate"], 60.0)

    def test_empty_events(self):
        result = build_time_dataset([])
        self.assertTrue(result.empty)

    def test_empty_minute(self):
        events = [
            {
                "timestamp": "2026-11-16 10:00:01",
                "level": "INFO"
            },
            {
                "timestamp": "2026-11-16 10:02:01",
                "level": "ERROR"
            }
        ]

        result = build_time_dataset(events)

        self.assertEqual(len(result), 3)
        self.assertEqual(result.iloc[1]["total_events"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
