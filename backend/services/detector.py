CATEGORY_RULES = {
    "DATABASE_ERROR": [
        "database", "sql", "mysql", "postgresql",
        "connection pool", "query failed"
    ],
    "NETWORK_ERROR": [
        "connection refused", "connection timeout",
        "network error", "host unreachable",
        "connection reset"
    ],
    "AUTHENTICATION_ERROR": [
        "login failed", "authentication failed",
        "unauthorized", "invalid password",
        "access denied"
    ],
    "PERFORMANCE_ISSUE": [
        "high response time", "slow response",
        "timeout", "high latency",
        "memory usage", "cpu usage"
    ],
    "SECURITY_EVENT": [
        "unauthorized access", "sql injection",
        "brute force", "suspicious activity",
        "security violation"
    ],
    "SYSTEM_ERROR": [
        "system failure", "application crashed",
        "out of memory", "disk full",
        "service unavailable"
    ],
    "APPLICATION_ERROR": [
        "http 500", "internal server error",
        "application error", "exception",
        "traceback"
    ]
}


SEVERITY_RULES = {
    "DEBUG": "LOW",
    "INFO": "LOW",
    "WARNING": "MEDIUM",
    "ERROR": "HIGH",
    "CRITICAL": "CRITICAL"
}


def classify_category(message: str) -> tuple[str, str]:
    message_lower = message.lower()

    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in message_lower:
                reason = f"Keyword detected: '{keyword}'"
                return category, reason

    return "UNKNOWN", "No matching detection rule"


def classify_severity(level: str) -> str:
    return SEVERITY_RULES.get(level.upper(), "LOW")


def detect_event(event: dict) -> dict:
    message = event.get("message", "")
    level = event.get("level", "UNKNOWN")

    category, reason = classify_category(message)
    severity = classify_severity(level)

    return {
        **event,
        "category": category,
        "severity": severity,
        "detection_reason": reason
    }


def detect_events(events: list[dict]) -> list[dict]:
    return [detect_event(event) for event in events]
