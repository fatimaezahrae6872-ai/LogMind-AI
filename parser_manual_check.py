from backend.services.parser import (
    parse_log_line,
    parse_log_lines
)


def test_valid_log():
    line = "2026-11-16 10:00:15 ERROR Database connection failed"
    result = parse_log_line(line)

    assert result["timestamp"] == "2026-11-16 10:00:15"
    assert result["level"] == "ERROR"
    assert result["message"] == "Database connection failed"
    assert result["is_parsed"] is True


def test_warning_normalization():
    result = parse_log_line(
        "2026-11-16 10:00:10 WARN High response time"
    )
    assert result["level"] == "WARNING"


def test_fatal_normalization():
    result = parse_log_line(
        "2026-11-16 10:00:20 FATAL Application crashed"
    )
    assert result["level"] == "CRITICAL"


def test_unknown_format():
    result = parse_log_line("Connection refused")

    assert result["level"] == "UNKNOWN"
    assert result["is_parsed"] is False


def test_empty_line():
    assert parse_log_line("   ") is None


def test_invalid_timestamp():
    result = parse_log_line(
        "2026-15-99 10:00:15 ERROR Invalid date"
    )
    assert result["is_parsed"] is False


def test_multiple_lines():
    lines = [
        "2026-11-16 10:00:01 INFO User logged in",
        "",
        "2026-11-16 10:00:15 ERROR Database failed"
    ]

    results = parse_log_lines(lines)

    assert len(results) == 2
    assert results[0]["line_number"] == 1
    assert results[1]["line_number"] == 3


if __name__ == "__main__":
    test_valid_log()
    test_warning_normalization()
    test_fatal_normalization()
    test_unknown_format()
    test_empty_line()
    test_invalid_timestamp()
    test_multiple_lines()

    print("All parser tests passed!")
