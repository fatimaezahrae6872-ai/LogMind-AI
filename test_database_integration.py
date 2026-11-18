
import os
import sqlite3
import tempfile
import unittest

from backend.core.database import (
    initialize_database,
    save_analysis_result
)
from backend.services.analysis_pipeline import (
    analyze_log_file,
    create_baseline_model
)


class TestDatabaseIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = create_baseline_model()

    def test_save_complete_analysis(self):

        with tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False
        ) as temp:
            db_path = temp.name

        try:
            initialize_database(db_path)

            result = analyze_log_file(
                "data/samples/application.log",
                model=self.model
            )

            file_id = save_analysis_result(
                result,
                db_path=db_path
            )

            connection = sqlite3.connect(db_path)

            counts = {}

            for table in [
                "log_files",
                "log_events",
                "incidents",
                "analysis_reports"
            ]:
                counts[table] = connection.execute(
                    f"SELECT COUNT(*) FROM {table}"
                ).fetchone()[0]

            connection.close()

            self.assertEqual(file_id, 1)
            self.assertEqual(counts["log_files"], 1)
            self.assertEqual(counts["log_events"], 7)
            self.assertEqual(counts["incidents"], 1)
            self.assertEqual(counts["analysis_reports"], 1)

        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == "__main__":
    unittest.main()

