import unittest

from backend.services.pipeline import analyze_log_file


class TestFullPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.result = analyze_log_file(
            "data/samples/application.log"
        )

    def test_file_ingestion(self):
        self.assertEqual(
            self.result["file"]["filename"],
            "application.log"
        )

    def test_parsing(self):
        self.assertEqual(
            self.result["summary"]["parsed_events"],
            7
        )

    def test_detection(self):
        self.assertEqual(
            self.result["summary"]["detected_events"],
            7
        )

    def test_incident_creation(self):
        self.assertEqual(
            self.result["summary"]["incident_count"],
            1
        )

    def test_critical_incident(self):
        incident = self.result["incidents"][0]

        self.assertEqual(
            incident["severity"],
            "CRITICAL"
        )

    def test_incident_events(self):
        incident = self.result["incidents"][0]

        self.assertEqual(incident["event_count"], 4)
        self.assertEqual(incident["trigger_count"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
