
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import (
    initialize_database,
    save_analysis_result
)


class TestLogMindAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # Create an isolated temporary database
        temp = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False
        )

        cls.db_path = temp.name
        temp.close()

        initialize_database(cls.db_path)

        # Redirect API database writes to the temporary database
        def save_to_test_database(result):
            return save_analysis_result(
                result,
                db_path=cls.db_path
            )

        cls.db_patcher = patch(
            "backend.api.routes_logs.save_analysis_result",
            side_effect=save_to_test_database
        )

        cls.db_patcher.start()

        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):

        cls.client_context.__exit__(None, None, None)

        cls.db_patcher.stop()

        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def test_upload_valid_log(self):

        with open(
            "data/samples/application.log",
            "rb"
        ) as log_file:

            response = self.client.post(
                "/api/v1/logs/analyze",
                files={
                    "file": (
                        "application.log",
                        log_file,
                        "text/plain"
                    )
                }
            )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["data"]["summary"]["total_events"],
            7
        )
        self.assertEqual(
            result["data"]["summary"]["total_incidents"],
            1
        )

    def test_reject_unsupported_extension(self):

        response = self.client.post(
            "/api/v1/logs/analyze",
            files={
                "file": (
                    "document.pdf",
                    b"PDF content",
                    "application/pdf"
                )
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_reject_empty_file(self):

        response = self.client.post(
            "/api/v1/logs/analyze",
            files={
                "file": (
                    "empty.log",
                    b"",
                    "text/plain"
                )
            }
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
