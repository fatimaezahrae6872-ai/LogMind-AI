
import re
from datetime import datetime
from typing import Optional


# Format attendu :
# 2026-11-16 10:00:15 ERROR Database connection failed

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2} "
    r"\d{2}:\d{2}:\d{2}) "
    r"(?P<level>INFO|DEBUG|WARNING|WARN|ERROR|CRITICAL|FATAL) "
    r"(?P<message>.+)$",
    re.IGNORECASE
)


def parse_log_line(line: str, line_number: int = 1) -> Optional[dict]:
    """
    Parse one raw log line into structured data.

    Returns None for empty lines.
    """

    line = line.strip()

    if not line:
        return None

    match = LOG_PATTERN.match(line)

    # Si le format n'est pas reconnu, on conserve le message
    if not match:
        return {
            "line_number": line_number,
            "timestamp": None,
            "level": "UNKNOWN",
            "message": line,
            "is_parsed": False
        }

    data = match.groupdict()

    # Normaliser le niveau
    level = data["level"].upper()

    if level == "WARN":
        level = "WARNING"

    if level == "FATAL":
        level = "CRITICAL"

    # Valider le timestamp
    try:
        timestamp = datetime.strptime(
            data["timestamp"],
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return {
            "line_number": line_number,
            "timestamp": None,
            "level": "UNKNOWN",
            "message": line,
            "is_parsed": False
        }

    return {
        "line_number": line_number,
        "timestamp": timestamp.isoformat(sep=" "),
        "level": level,
        "message": data["message"].strip(),
        "is_parsed": True
    }


def parse_log_lines(lines: list[str]) -> list[dict]:
    """
    Parse multiple log lines.
    Empty lines are ignored.
    """

    parsed_logs = []

    for line_number, line in enumerate(lines, start=1):
        result = parse_log_line(line, line_number)

        if result is not None:
            parsed_logs.append(result)

    return parsed_logs
