
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.routes_logs import router


# Create a lightweight test application
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestDiagnosisAPI(unittest.TestCase):

    def setUp(self):
        self.incident = {
            "id": 1,
            "title": "System Error Incident",
            "events": []
        }

        self.diagnosis = {
            "diagnosis_id": 1,
            "incident_id": 1,
            "summary": "Database connection failure.",
            "root_causes": [
                {
                    "hypothesis": "Database connectivity issue.",
                    "evidence": ["Database connection failed"],
                    "confidence": 0.8
                }
            ],
            "recommendations": [
                "Check database configuration.",
                "Monitor database connectivity."
            ],
            "generated_at": "2026-11-17 16:51:04"
        }

    @patch("backend.core.database.get_latest_diagnosis")
    @patch("backend.api.routes_logs.get_incident_with_events")
    def test_get_existing_diagnosis(
        self,
        mock_get_incident,
        mock_get_diagnosis
    ):
        mock_get_incident.return_value = self.incident
        mock_get_diagnosis.return_value = self.diagnosis

        response = client.get(
            "/api/v1/logs/incidents/1/diagnosis"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["status"], "success")
        self.assertEqual(data["incident_id"], 1)
        self.assertEqual(
            data["diagnosis"]["diagnosis_id"], 1
        )

    @patch("backend.api.routes_logs.get_incident_with_events")
    def test_incident_not_found(self, mock_get_incident):
        mock_get_incident.return_value = None

        response = client.get(
            "/api/v1/logs/incidents/9999/diagnosis"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["detail"],
            "Incident not found."
        )

    @patch("backend.core.database.get_latest_diagnosis")
    @patch("backend.api.routes_logs.get_incident_with_events")
    def test_diagnosis_not_found(
        self,
        mock_get_incident,
        mock_get_diagnosis
    ):
        mock_get_incident.return_value = self.incident
        mock_get_diagnosis.return_value = None

        response = client.get(
            "/api/v1/logs/incidents/2/diagnosis"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["detail"],
            "No diagnosis found for this incident."
        )


if __name__ == "__main__":
    unittest.main()
