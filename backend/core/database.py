
import sqlite3
import json
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database location
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "logmind.db"


def get_connection(db_path=DB_PATH):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=DB_PATH):

    connection = get_connection(db_path)

    try:
        connection.executescript("""

            CREATE TABLE IF NOT EXISTS log_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER,
                total_lines INTEGER,
                upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'COMPLETED'
            );

            CREATE TABLE IF NOT EXISTS log_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_file_id INTEGER NOT NULL,
                timestamp TEXT,
                level TEXT,
                message TEXT,
                category TEXT,
                severity TEXT,
                is_parsed INTEGER,
                raw_data TEXT,

                FOREIGN KEY (log_file_id)
                    REFERENCES log_files(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_file_id INTEGER NOT NULL,
                incident_code TEXT NOT NULL,
                title TEXT,
                severity TEXT,
                category TEXT,
                first_seen TEXT,
                last_seen TEXT,
                event_count INTEGER,
                trigger_count INTEGER,
                correlation_reason TEXT,
                details_json TEXT,

                FOREIGN KEY (log_file_id)
                    REFERENCES log_files(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                summary TEXT,
                root_causes TEXT,
                recommendations TEXT,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (incident_id)
                    REFERENCES incidents(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_file_id INTEGER NOT NULL,
                report_content TEXT,
                generated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (log_file_id)
                    REFERENCES log_files(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_events_log_file
            ON log_events(log_file_id);

            CREATE INDEX IF NOT EXISTS idx_incidents_log_file
            ON incidents(log_file_id);

        """)

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print("LogMind AI database initialized successfully!")
    print(f"Database location: {DB_PATH}")

def save_analysis_result(result, db_path=DB_PATH):
    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()

        # 1. Save uploaded file information
        file_info = result["file"]

        cursor.execute("""
            INSERT INTO log_files (
                filename,
                extension,
                size_bytes,
                total_lines,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            file_info["filename"],
            file_info["extension"],
            file_info["size_bytes"],
            file_info["total_lines"],
            "COMPLETED"
        ))

        log_file_id = cursor.lastrowid

        # 2. Save detected log events
        for event in result["events"]:

            cursor.execute("""
                INSERT INTO log_events (
                    log_file_id,
                    timestamp,
                    level,
                    message,
                    category,
                    severity,
                    is_parsed,
                    raw_data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_file_id,
                str(event.get("timestamp", "")),
                event.get("level"),
                event.get("message"),
                event.get("category"),
                event.get("severity"),
                int(bool(event.get("is_parsed", False))),
                json.dumps(event, default=str)
            ))

        # 3. Save correlated incidents
        for incident in result["incidents"]:

            cursor.execute("""
                INSERT INTO incidents (
                    log_file_id,
                    incident_code,
                    title,
                    severity,
                    category,
                    first_seen,
                    last_seen,
                    event_count,
                    trigger_count,
                    correlation_reason,
                    details_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_file_id,
                incident.get("incident_id"),
                incident.get("title"),
                incident.get("severity"),
                incident.get("primary_category"),
                str(incident.get("first_seen", "")),
                str(incident.get("last_seen", "")),
                incident.get("event_count", 0),
                incident.get("trigger_count", 0),
                incident.get("correlation_reason"),
                json.dumps(incident, default=str)
            ))

        # 4. Save analysis report
        report_content = {
            "summary": result["summary"],
            "statistics": result["statistics"],
            "anomalies": result["anomalies"]
        }

        cursor.execute("""
            INSERT INTO analysis_reports (
                log_file_id,
                report_content
            )
            VALUES (?, ?)
        """, (
            log_file_id,
            json.dumps(report_content, default=str)
        ))

        connection.commit()

        return log_file_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
def get_incident_with_events(incident_id, db_path=DB_PATH):
    connection = get_connection(db_path)

    try:
        incident_row = connection.execute("""
            SELECT *
            FROM incidents
            WHERE id = ?
        """, (incident_id,)).fetchone()

        if incident_row is None:
            return None

        incident = dict(incident_row)

        events = json.loads(incident["details_json"]).get("events", [])

        incident["events"] = events
        incident["primary_category"] = incident["category"]

        return incident

    finally:
        connection.close()


def save_diagnosis(incident_id, diagnosis, db_path=DB_PATH):
    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO diagnoses (
                incident_id,
                summary,
                root_causes,
                recommendations
            )
            VALUES (?, ?, ?, ?)
        """, (
            incident_id,
            diagnosis["summary"],
            json.dumps(diagnosis["root_causes"], ensure_ascii=False),
            json.dumps(diagnosis["recommendations"], ensure_ascii=False)
        ))

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def get_latest_diagnosis(incident_id, db_path=DB_PATH):
    """Retrieve the latest saved AI diagnosis for an incident."""

    connection = get_connection(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, incident_id, summary, root_causes,
                   recommendations, generated_at
            FROM diagnoses
            WHERE incident_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (incident_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "diagnosis_id": row[0],
            "incident_id": row[1],
            "summary": row[2],
            "root_causes": json.loads(row[3]),
            "recommendations": json.loads(row[4]),
            "generated_at": row[5]
        }

    finally:
        connection.close()
