
from backend.core.database import get_connection

connection = get_connection()

tables = [
    "log_files",
    "log_events",
    "incidents",
    "analysis_reports"
]

print("\n========== LOGMIND AI DATABASE ==========\n")

for table in tables:
    count = connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count} records")

print("\n========== SAVED FILES ==========\n")

files = connection.execute("""
    SELECT id, filename, status, upload_date
    FROM log_files
    ORDER BY id DESC
""").fetchall()

for file in files:
    print(dict(file))

connection.close()
