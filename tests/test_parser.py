from backend.services.parser import (
    parse_log_line,
    parse_log_lines
)


def test_parse_valid_log():
    line = "2026-11-16 10:00:15 ERROR Database connection failed"
    result = parse_log_line(line, 1)

    assert result["level"] == "ERROR"
    assert result["message"] == "Database connection failed"
    assert result["is_parsed"] is True


def test_warn_normalization():
    line = "2026-11-16 10:00:15 WARN Slow response"
    result = parse_log_line(line)

    assert result["level"] == "WARNING"


def test_fatal_normalization():
    line = "2026-11-16 10:00:15 FATAL Application crashed"
    result = parse_log_line(line)

    assert result["level"] == "CRITICAL"


def test_unknown_format():
    result = parse_log_line("Unexpected log format")

    assert result["level"] == "UNKNOWN"
    assert result["is_parsed"] is False
def test_invalid_timestamp():
    result = parse_log_line(
        "2026-15-99 10:00:15 ERROR Invalid date"
    )

    assert result["is_parsed"] is False
    assert result["level"] == "UNKNOWN"
def test_empty_line():
    result = parse_log_line("")

    assert result is None


def test_parse_multiple_lines():
    lines = [
        "2026-11-16 10:00:01 INFO Application started",
        "",
        "2026-11-16 10:00:15 ERROR Database connection failed"
    ]

    results = parse_log_lines(lines)

    assert len(results) == 2
    assert results[0]["level"] == "INFO"
    assert results[1]["level"] == "ERROR"
    assert results[1]["line_number"] == 3