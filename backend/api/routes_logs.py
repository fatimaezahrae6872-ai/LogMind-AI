
import os
import tempfile

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Request,
    Query
)

from backend.core.database import (
    save_analysis_result,
    get_connection,
    get_incident_with_events,
    save_diagnosis
)

from backend.services.analysis_pipeline import analyze_log_file

from backend.services.ai_agent import (
    diagnose_incident,
    AIAgentError
)


router = APIRouter(
    prefix="/api/v1/logs",
    tags=["Logs"]
)

ALLOWED_EXTENSIONS = {".log", ".txt", ".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024


# ==========================================
# 1. ANALYZE UPLOADED LOG FILE
# ==========================================

@router.post("/analyze")
async def analyze_uploaded_log(
    request: Request,
    file: UploadFile = File(...)
):

    extension = os.path.splitext(file.filename or "")[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use .log, .txt or .csv"
        )

    temp_path = None

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 10 MB limit."
            )

        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=extension,
            delete=False
        ) as temp_file:

            temp_file.write(content)
            temp_path = temp_file.name

        ml_model = request.app.state.ml_model

        result = analyze_log_file(
            temp_path,
            model=ml_model
        )

        result["file"]["filename"] = os.path.basename(
            file.filename or "uploaded.log"
        )

        log_file_id = save_analysis_result(result)

        return {
            "status": "success",
            "message": "Log analysis completed successfully",
            "log_file_id": log_file_id,
            "data": result
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred during log analysis."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        await file.close()


# ==========================================
# 2. GET ANALYZED LOG FILES
# ==========================================

@router.get("")
def get_logs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):

    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                lf.id,
                lf.filename,
                lf.extension,
                lf.size_bytes,
                lf.total_lines,
                lf.upload_date,
                lf.status,

                (
                    SELECT COUNT(*)
                    FROM log_events e
                    WHERE e.log_file_id = lf.id
                ) AS total_events,

                (
                    SELECT COUNT(*)
                    FROM incidents i
                    WHERE i.log_file_id = lf.id
                ) AS total_incidents

            FROM log_files lf

            ORDER BY lf.id DESC

            LIMIT ? OFFSET ?

        """, (limit, offset)).fetchall()

        total = connection.execute("""
            SELECT COUNT(*) FROM log_files
        """).fetchone()[0]

        return {
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [dict(row) for row in rows]
        }

    finally:
        connection.close()


# ==========================================
# 3. GET DETECTED INCIDENTS
# ==========================================

@router.get("/incidents")
def get_incidents(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):

    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                i.id,
                i.incident_code,
                i.title,
                i.severity,
                i.category,
                i.first_seen,
                i.last_seen,
                i.event_count,
                i.trigger_count,
                i.correlation_reason,
                i.log_file_id,
                lf.filename

            FROM incidents i

            JOIN log_files lf
                ON i.log_file_id = lf.id

            ORDER BY i.id DESC

            LIMIT ? OFFSET ?

        """, (limit, offset)).fetchall()

        total = connection.execute("""
            SELECT COUNT(*) FROM incidents
        """).fetchone()[0]

        return {
            "status": "success",
            "total": total,
            "limit": limit,
            "offset": offset,
            "data": [dict(row) for row in rows]
        }

    finally:
        connection.close()


# ==========================================
# 4. GENERATE AI DIAGNOSIS FOR AN INCIDENT
# ==========================================

@router.post("/incidents/{incident_id}/diagnose")
def diagnose_stored_incident(incident_id: int):

    # Step 1: Retrieve incident from SQLite
    incident = get_incident_with_events(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found."
        )

    # Step 2: Generate AI diagnosis using Ollama
    try:
        diagnosis = diagnose_incident(incident)

    except AIAgentError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    # Step 3: Save diagnosis in SQLite
    try:
        diagnosis_id = save_diagnosis(
            incident_id,
            diagnosis
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save AI diagnosis."
        )

    # Step 4: Return diagnosis
    return {
        "status": "success",
        "message": "AI diagnosis generated successfully.",
        "diagnosis_id": diagnosis_id,
        "incident_id": incident_id,
        "diagnosis": diagnosis
    }

@router.get("/incidents/{incident_id}/diagnosis")
def get_incident_diagnosis(incident_id: int):
    # Check whether the incident exists
    incident = get_incident_with_events(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found."
        )

    from backend.core.database import get_latest_diagnosis

    diagnosis = get_latest_diagnosis(incident_id)

    if diagnosis is None:
        raise HTTPException(
            status_code=404,
            detail="No diagnosis found for this incident."
        )

    return {
        "status": "success",
        "incident_id": incident_id,
        "diagnosis": diagnosis
    }

@router.get("/reports/summary")
def get_reports_summary():
    connection = get_connection()

    try:
        # 1. General KPIs
        total_files = connection.execute(
            "SELECT COUNT(*) FROM log_files"
        ).fetchone()[0]

        total_events = connection.execute(
            "SELECT COUNT(*) FROM log_events"
        ).fetchone()[0]

        total_incidents = connection.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]

        total_diagnoses = connection.execute(
            "SELECT COUNT(*) FROM diagnoses"
        ).fetchone()[0]

        # 2. Log level distribution
        level_rows = connection.execute("""
            SELECT level, COUNT(*) AS count
            FROM log_events
            GROUP BY level
            ORDER BY count DESC
        """).fetchall()

        log_levels = {
            row["level"]: row["count"]
            for row in level_rows
        }

        # 3. Incident severity distribution
        severity_rows = connection.execute("""
            SELECT severity, COUNT(*) AS count
            FROM incidents
            GROUP BY severity
            ORDER BY count DESC
        """).fetchall()

        severities = {
            row["severity"]: row["count"]
            for row in severity_rows
        }

        # 4. Incident category distribution
        category_rows = connection.execute("""
            SELECT category, COUNT(*) AS count
            FROM incidents
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()

        categories = {
            row["category"]: row["count"]
            for row in category_rows
        }

        # 5. File status distribution
        status_rows = connection.execute("""
            SELECT status, COUNT(*) AS count
            FROM log_files
            GROUP BY status
        """).fetchall()

        file_statuses = {
            row["status"]: row["count"]
            for row in status_rows
        }

        # 6. Error rate: ERROR + CRITICAL / total events
        error_events = (
            log_levels.get("ERROR", 0)
            + log_levels.get("CRITICAL", 0)
        )

        error_rate = (
            round((error_events / total_events) * 100, 2)
            if total_events > 0
            else 0
        )

        return {
            "status": "success",
            "data": {
                "kpis": {
                    "total_files": total_files,
                    "total_events": total_events,
                    "total_incidents": total_incidents,
                    "total_diagnoses": total_diagnoses,
                    "error_events": error_events,
                    "error_rate": error_rate
                },
                "log_levels": log_levels,
                "severities": severities,
                "categories": categories,
                "file_statuses": file_statuses
            }
        }

    finally:
        connection.close()
