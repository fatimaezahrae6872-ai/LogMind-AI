
import sqlite3
import tempfile
import unittest
import os

from backend.core.database import initialize_database


class TestDatabase(unittest.TestCase):

    def test_database_tables_creation(self):

        temp = tempfile.NamedTemporaryFile(
            suffix=".db",
            delete=False
        )
        db_path = temp.name
        temp.close()

        try:
            initialize_database(db_path)

            connection = sqlite3.connect(db_path)

            cursor = connection.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
            """)

            tables = {row[0] for row in cursor.fetchall()}

            expected_tables = {
                "log_files",
                "log_events",
                "incidents",
                "diagnoses",
                "analysis_reports"
            }

            self.assertEqual(tables, expected_tables)

            connection.close()

        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


if __name__ == "__main__":
    unittest.main()
