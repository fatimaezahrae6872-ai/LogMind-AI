
import tempfile
import unittest
from pathlib import Path

from backend.services.ingestion import (
    ingest_log_file,
    LogIngestionError,
    MAX_FILE_SIZE
)


class TestLogIngestionValidation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_file_not_found(self):
        path = self.test_dir / "unknown.log"

        with self.assertRaises(LogIngestionError):
            ingest_log_file(str(path))

    def test_unsupported_extension(self):
        path = self.test_dir / "document.pdf"
        path.write_text("Some content", encoding="utf-8")

        with self.assertRaises(LogIngestionError):
            ingest_log_file(str(path))

    def test_empty_file(self):
        path = self.test_dir / "empty.log"
        path.write_text("", encoding="utf-8")

        with self.assertRaises(LogIngestionError):
            ingest_log_file(str(path))

    def test_file_too_large(self):
        path = self.test_dir / "large.log"
        path.write_bytes(b"A" * (MAX_FILE_SIZE + 1))

        with self.assertRaises(LogIngestionError):
            ingest_log_file(str(path))


if __name__ == "__main__":
    unittest.main(verbosity=2)
