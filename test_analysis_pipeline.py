import unittest

from backend.services.analysis_pipeline import analyze_log_file


class TestAnalysisPipeline(unittest.TestCase):

    def test_complete_pipeline(self):
        result = analyze_log_file(
            "data/samples/application.log"
        )

        self.assertEqual(
            result["file"]["filename"],
            "application.log"
        )

        self.assertEqual(
            result["summary"]["total_events"],
            7
        )

        self.assertEqual(
            result["statistics"]["error_rate"],
            42.86
        )

        self.assertEqual(
            result["summary"]["total_incidents"],
            1
        )

        self.assertEqual(
            len(result["anomalies"]),
            1
        )

    def test_critical_event_is_detected(self):
        result = analyze_log_file(
            "data/samples/application.log"
        )

        self.assertTrue(
            any(
                item["critical_rule"]
                for item in result["anomalies"]
            )
        )

        self.assertEqual(
            result["anomalies"][0]["final_prediction"],
            "ANOMALY"
        )


if __name__ == "__main__":
    unittest.main()
