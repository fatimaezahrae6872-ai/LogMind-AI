import pytest

from backend.services.ingestion import (
    ingest_log_file,
    LogIngestionError
)

import backend.services.ingestion as ingestion


def test_ingest_valid_log_file(tmp_path):
    log_file = tmp_path / "sample.log"

    log_file.write_text(
        "INFO Application started\n"
        "\n"
        "ERROR Database connection failed\n",
        encoding="utf-8"
    )

    result = ingest_log_file(str(log_file))

    assert result.filename == "sample.log"
    assert result.extension == ".log"
    assert result.total_lines == 3
    assert result.empty_lines == 1
    assert len(result.content) == 3


def test_missing_file():
    with pytest.raises(
        LogIngestionError,
        match="File does not exist"
    ):
        ingest_log_file("unknown.log")


def test_unsupported_extension(tmp_path):
    file_path = tmp_path / "document.json"
    file_path.write_text('{"test": true}', encoding="utf-8")

    with pytest.raises(
        LogIngestionError,
        match="Unsupported file extension"
    ):
        ingest_log_file(str(file_path))


def test_empty_file(tmp_path):
    file_path = tmp_path / "empty.log"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(
        LogIngestionError,
        match="The file is empty"
    ):
        ingest_log_file(str(file_path))


def test_file_exceeds_size_limit(tmp_path, monkeypatch):
    file_path = tmp_path / "large.log"
    file_path.write_text("1234567890", encoding="utf-8")

    monkeypatch.setattr(ingestion, "MAX_FILE_SIZE", 5)

    with pytest.raises(
        LogIngestionError,
        match="10 MB limit"
    ):
        ingest_log_file(str(file_path))
