
import requests

from .config import API_BASE_URL, REQUEST_TIMEOUT


def _handle_response(response):
    """Check the HTTP response and return JSON data."""
    try:
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as exc:
        try:
            details = response.json()
            message = details.get("detail", str(exc))
        except ValueError:
            message = response.text or str(exc)

        raise RuntimeError(f"API Error ({response.status_code}): {message}")

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Connection error: {exc}")


def check_health():
    """Check whether the FastAPI backend is running."""
    response = requests.get(
        f"{API_BASE_URL}/api/v1/health",
        timeout=REQUEST_TIMEOUT
    )
    return _handle_response(response)


def analyze_log(uploaded_file):
    """Upload and analyze a log file."""
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream"
        )
    }

    response = requests.post(
        f"{API_BASE_URL}/api/v1/logs/analyze",
        files=files,
        timeout=120
    )
    return _handle_response(response)


def get_logs(skip=0, limit=20):
    """Retrieve analyzed log files."""
    response = requests.get(
        f"{API_BASE_URL}/api/v1/logs",
        params={"skip": skip, "limit": limit},
        timeout=REQUEST_TIMEOUT
    )
    return _handle_response(response)


def get_incidents(skip=0, limit=20):
    """Retrieve detected incidents."""
    response = requests.get(
        f"{API_BASE_URL}/api/v1/logs/incidents",
        params={"skip": skip, "limit": limit},
        timeout=REQUEST_TIMEOUT
    )
    return _handle_response(response)


def diagnose_incident(incident_id):
    """Generate an AI diagnosis for an incident."""
    response = requests.post(
        f"{API_BASE_URL}/api/v1/logs/incidents/{incident_id}/diagnose",
        timeout=150
    )
    return _handle_response(response)


def get_incident_diagnosis(incident_id):
    """Retrieve the latest saved diagnosis."""
    response = requests.get(
        f"{API_BASE_URL}/api/v1/logs/incidents/{incident_id}/diagnosis",
        timeout=REQUEST_TIMEOUT
    )
    return _handle_response(response)

def get_report_summary():
    response = requests.get(
        f"{API_BASE_URL}/api/v1/logs/reports/summary",
        timeout=REQUEST_TIMEOUT
    )
    return _handle_response(response)
