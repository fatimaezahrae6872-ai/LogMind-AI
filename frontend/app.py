
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from frontend.api_client import (
    check_health,
    get_logs,
    get_incidents,
    analyze_log,
    get_incident_diagnosis,
    diagnose_incident,
    get_report_summary
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="LogMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #172554;
        border-right: 1px solid #263b70;
    }

    [data-testid="stSidebar"] h1 {
        color: #67e8f9;
    }

    .main-title {
        color: #f8fafc;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 25px;
    }

    [data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 18px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    [data-testid="stMetricValue"] {
        color: #67e8f9;
    }

    .section-title {
        color: #e2e8f0;
        font-size: 20px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    .status-card {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 10px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #334155;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# 🧠 LogMind AI")
    st.caption("Intelligent Log Analysis Platform")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Log Analyzer",
            "Incident Explorer",
            "AI Diagnosis",
            "Reports"
        ],
        index=0
    )

    st.divider()

    st.caption("LOCAL AI PLATFORM")
    st.caption("Version 1.0.0")


# ==========================================
# DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Monitor your logs, detect incidents and analyze system health.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------
    # LOAD DATA FROM FASTAPI
    # --------------------------------------

    try:
        logs_response = get_logs(limit=100)
        incidents_response = get_incidents(limit=100)

        logs = logs_response.get("data", [])
        incidents = incidents_response.get("data", [])

        total_files = logs_response.get("total", len(logs))
        total_incidents = incidents_response.get(
            "total", len(incidents)
        )

        critical_count = sum(
            1 for incident in incidents
            if incident.get("severity") == "CRITICAL"
        )

        total_events = sum(
            log.get("total_events") or 0
            for log in logs
        )

        # ----------------------------------
        # KPI CARDS
        # ----------------------------------

        st.markdown(
            '<div class="section-title">System Overview</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Files Analyzed",
            total_files
        )

        col2.metric(
            "Events Processed",
            f"{total_events:,}"
        )

        col3.metric(
            "Incidents Detected",
            total_incidents
        )

        col4.metric(
            "Critical Incidents",
            critical_count
        )

        st.divider()

        # ----------------------------------
        # SYSTEM STATUS
        # ----------------------------------

        st.markdown(
            '<div class="section-title">System Status</div>',
            unsafe_allow_html=True
        )

        status_col1, status_col2 = st.columns(2)

        with status_col1:
            try:
                health = check_health()

                st.success(
                    f"Backend: {health.get('status', 'Unknown').upper()}"
                )

            except Exception:
                st.error("Backend: OFFLINE")

        with status_col2:
            try:
                ollama_response = requests.get(
                    "http://127.0.0.1:11434/api/tags",
                    timeout=2
                )
                ollama_response.raise_for_status()

                models = ollama_response.json().get("models", [])

                model_available = any(
                    model.get("name", "").startswith("qwen2.5:1.5b")
                    for model in models
                )

                if model_available:
                    st.success("Ollama: ONLINE — Qwen2.5 1.5B available")
                else:
                    st.warning("Ollama: ONLINE — model not found")

            except requests.exceptions.RequestException:
                st.error("Ollama: OFFLINE")

        st.divider()

        # ----------------------------------
        # INCIDENT ANALYTICS
        # ----------------------------------

        left_col, right_col = st.columns(2)

        with left_col:

            st.markdown(
                '<div class="section-title">Incidents by Severity</div>',
                unsafe_allow_html=True
            )

            severity_order = [
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW"
            ]

            severity_counts = {
                severity: sum(
                    1 for incident in incidents
                    if incident.get("severity") == severity
                )
                for severity in severity_order
            }

            severity_df = pd.DataFrame({
                "Severity": severity_order,
                "Incidents": [
                    severity_counts[severity]
                    for severity in severity_order
                ]
            })

            if total_incidents > 0:
                st.bar_chart(
                    severity_df.set_index("Severity"),
                    y="Incidents"
                )
            else:
                st.info("No incidents detected yet.")

        with right_col:

            st.markdown(
                '<div class="section-title">Incidents by Category</div>',
                unsafe_allow_html=True
            )

            category_counts = {}

            for incident in incidents:
                category = incident.get("category") or "UNKNOWN"

                category_counts[category] = (
                    category_counts.get(category, 0) + 1
                )

            if category_counts:
                category_df = pd.DataFrame({
                    "Category": list(category_counts.keys()),
                    "Incidents": list(category_counts.values())
                })

                st.bar_chart(
                    category_df.set_index("Category"),
                    y="Incidents"
                )
            else:
                st.info("No category data available.")

        st.divider()

        # ----------------------------------
        # RECENT INCIDENTS
        # ----------------------------------

        st.markdown(
            '<div class="section-title">Recent Incidents</div>',
            unsafe_allow_html=True
        )

        if incidents:

            incident_rows = []

            for incident in incidents[:10]:
                incident_rows.append({
                    "ID": incident.get("incident_code"),
                    "Title": incident.get("title"),
                    "Severity": incident.get("severity"),
                    "Category": incident.get("category"),
                    "File": incident.get("filename"),
                    "Events": incident.get("event_count")
                })

            incident_df = pd.DataFrame(incident_rows)

            st.dataframe(
                incident_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No incidents available.")

        st.caption(
            "Dashboard data is retrieved from the LogMind AI backend."
        )

    except Exception as error:

        st.error("Unable to load dashboard data.")

        st.code(str(error))

        st.info(
            "Make sure the FastAPI backend is running on port 8000."
        )



# ==========================================
# LOG ANALYZER
# ==========================================

elif page == "Log Analyzer":

    st.title("📂 Log Analyzer")

    st.caption(
        "Upload your application logs and let LogMind AI analyze them."
    )

    st.divider()

    st.subheader("Upload Log File")

    uploaded_file = st.file_uploader(
        "Choose a log file",
        type=["log", "txt", "csv"],
        help="Supported formats: LOG, TXT and CSV. Maximum size: 10 MB."
    )

    if uploaded_file is not None:

        file_size_mb = uploaded_file.size / (1024 * 1024)

        col1, col2, col3 = st.columns(3)

        col1.metric("Filename", uploaded_file.name)
        col2.metric("Size", f"{file_size_mb:.2f} MB")
        col3.metric("Format", uploaded_file.name.split(".")[-1].upper())

        if uploaded_file.size > 10 * 1024 * 1024:

            st.error("File exceeds the maximum size of 10 MB.")

        else:

            st.success("File ready for analysis.")

            if st.button(
                "🚀 Analyze Logs",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "LogMind AI is analyzing your logs..."
                ):

                    try:
                        result = analyze_log(uploaded_file)

                        st.session_state["last_analysis"] = result

                        st.success("Analysis completed successfully!")

                    except Exception as error:

                        st.error("Analysis failed.")
                        st.exception(error)

    
    # --------------------------------------
    # DISPLAY ANALYSIS RESULT
    # --------------------------------------

    if "last_analysis" in st.session_state:

        result = st.session_state["last_analysis"]
        data = result.get("data", {})

        if result.get("status") == "success":

            st.divider()
            st.subheader("📊 Analysis Results")

            summary = data.get("summary", {})
            stats = data.get("statistics", {})

            # ==================================
            # SUMMARY METRICS
            # ==================================

            st.markdown("### Analysis Overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Total Events",
                summary.get("total_events", 0)
            )

            c2.metric(
                "Incidents",
                summary.get("total_incidents", 0)
            )

            c3.metric(
                "Anomaly Windows",
                summary.get("anomaly_windows", 0)
            )

            c4.metric(
                "Error Rate",
                f"{stats.get('error_rate', 0):.2f}%"
            )

            st.caption(
                f"File: {data.get('file', {}).get('filename', 'Unknown')} "
                f"| ID: {result.get('log_file_id', 'N/A')}"
            )

            st.divider()

            # ==================================
            # LOG LEVEL STATISTICS
            # ==================================

            st.markdown("### Log Level Distribution")

            levels = [
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL"
            ]

            level_values = [
                stats.get("info_count", 0),
                stats.get("warning_count", 0),
                stats.get("error_count", 0),
                stats.get("critical_count", 0)
            ]

            level_col1, level_col2 = st.columns(2)

            with level_col1:

                level_df = pd.DataFrame({
                    "Level": levels,
                    "Events": level_values
                })

                st.bar_chart(
                    level_df.set_index("Level"),
                    y="Events"
                )

            with level_col2:

                st.markdown("#### Event Counts")

                for level, count in zip(levels, level_values):

                    st.write(f"**{level}**")

                    st.progress(
                        count / max(sum(level_values), 1)
                    )

                    st.caption(f"{count} events")

            st.divider()

            # ==================================
            # CATEGORY DISTRIBUTION
            # ==================================

            st.markdown("### Event Categories")

            category_counts = stats.get("category_counts", {})

            if category_counts:

                category_df = pd.DataFrame({
                    "Category": list(category_counts.keys()),
                    "Events": list(category_counts.values())
                })

                st.bar_chart(
                    category_df.set_index("Category"),
                    y="Events"
                )

            else:
                st.info("No category statistics available.")

            st.divider()

            # ==================================
            # ANOMALY DETECTION
            # ==================================

            st.markdown("### 🤖 Hybrid Anomaly Detection")

            anomalies = data.get("anomalies", [])

            if anomalies:

                for index, anomaly in enumerate(anomalies, start=1):

                    prediction = anomaly.get(
                        "final_prediction", "UNKNOWN"
                    )

                    with st.container(border=True):

                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Window",
                            index
                        )

                        col2.metric(
                            "ML Prediction",
                            anomaly.get("ml_prediction", "N/A")
                        )

                        col3.metric(
                            "Final Prediction",
                            prediction
                        )

                        st.write(
                            f"**Timestamp:** {anomaly.get('timestamp', 'N/A')}"
                        )

                        st.write(
                            f"**Anomaly Score:** "
                            f"{anomaly.get('anomaly_score', 'N/A')}"
                        )

                        st.write(
                            f"**Critical Rule:** "
                            f"{'Triggered' if anomaly.get('critical_rule') else 'Not triggered'}"
                        )

                        if prediction == "ANOMALY":
                            st.error("Anomalous window detected")
                        else:
                            st.success("Normal window")

            else:
                st.info("No anomaly windows detected.")

            st.divider()

            # ==================================
            # INCIDENT DETAILS
            # ==================================

            st.markdown("### 🚨 Detected Incidents")

            incidents = data.get("incidents", [])

            if incidents:

                for incident in incidents:

                    severity = incident.get("severity", "UNKNOWN")

                    with st.expander(
                        f"{incident.get('incident_id', 'INC')} — "
                        f"{incident.get('title', 'Incident')} "
                        f"[{severity}]",
                        expanded=True
                    ):

                        st.write(
                            f"**Category:** "
                            f"{incident.get('primary_category', 'N/A')}"
                        )

                        st.write(
                            f"**First seen:** "
                            f"{incident.get('first_seen', 'N/A')}"
                        )

                        st.write(
                            f"**Last seen:** "
                            f"{incident.get('last_seen', 'N/A')}"
                        )

                        st.write(
                            f"**Events:** {incident.get('event_count', 0)}"
                        )

                        st.write(
                            f"**Trigger events:** "
                            f"{incident.get('trigger_count', 0)}"
                        )

                        st.info(
                            incident.get(
                                "correlation_reason",
                                "No correlation details available."
                            )
                        )

                        st.markdown("#### Related Events")

                        incident_events = incident.get("events", [])

                        if incident_events:

                            incident_df = pd.DataFrame([
                                {
                                    "Line": event.get("line_number"),
                                    "Timestamp": event.get("timestamp"),
                                    "Level": event.get("level"),
                                    "Category": event.get("category"),
                                    "Message": event.get("message")
                                }
                                for event in incident_events
                            ])

                            st.dataframe(
                                incident_df,
                                use_container_width=True,
                                hide_index=True
                            )

            else:
                st.success("No incidents detected.")

            st.divider()

            # ==================================
            # ALL LOG EVENTS
            # ==================================

            st.markdown("### 📋 All Parsed Events")

            events = data.get("events", [])

            if events:

                events_df = pd.DataFrame([
                    {
                        "Line": event.get("line_number"),
                        "Timestamp": event.get("timestamp"),
                        "Level": event.get("level"),
                        "Severity": event.get("severity"),
                        "Category": event.get("category"),
                        "Message": event.get("message"),
                        "Detection Reason": event.get("detection_reason")
                    }
                    for event in events
                ])

                st.dataframe(
                    events_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No events available.")

            # ==================================
            # EXPORT RESULTS
            # ==================================

            st.divider()

            st.markdown("### Export Analysis")

            json_data = pd.Series(result).to_json(
                force_ascii=False,
                indent=4
            )

            st.download_button(
                label="⬇️ Download Analysis JSON",
                data=json_data,
                file_name="logmind_analysis.json",
                mime="application/json"
            )

        else:

            st.error(
                result.get("message", "Analysis was not successful.")
            )

# ==========================================
# INCIDENT EXPLORER
# ==========================================

elif page == "Incident Explorer":

    st.title("🚨 Incident Explorer")

    st.caption(
        "Explore, filter and inspect incidents detected by LogMind AI."
    )

    st.divider()

    try:
        response = get_incidents(limit=100)
        incidents = response.get("data", [])

        if not incidents:

            st.success("No incidents detected yet.")

        else:

            # ----------------------------------
            # FILTERS
            # ----------------------------------

            st.subheader("Incident Overview")

            severity_options = [
                "ALL",
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW"
            ]

            selected_severity = st.selectbox(
                "Filter by severity",
                severity_options
            )

            filtered_incidents = [
                incident for incident in incidents
                if selected_severity == "ALL"
                or incident.get("severity") == selected_severity
            ]

            # ----------------------------------
            # SUMMARY METRICS
            # ----------------------------------

            critical_total = sum(
                1 for incident in incidents
                if incident.get("severity") == "CRITICAL"
            )

            high_total = sum(
                1 for incident in incidents
                if incident.get("severity") == "HIGH"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Incidents", len(incidents))
            col2.metric("Critical", critical_total)
            col3.metric("High", high_total)

            st.divider()

            # ----------------------------------
            # INCIDENT TABLE
            # ----------------------------------

            st.subheader("Detected Incidents")

            rows = []

            for incident in filtered_incidents:

                rows.append({
                    "ID": incident.get("incident_code"),
                    "Title": incident.get("title"),
                    "Severity": incident.get("severity"),
                    "Category": incident.get("category"),
                    "Events": incident.get("event_count"),
                    "File": incident.get("filename")
                })

            if rows:

                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No incidents match this severity.")

            st.divider()

            # ----------------------------------
            # INCIDENT DETAILS
            # ----------------------------------

            st.subheader("Incident Details")

            if filtered_incidents:

                selected_code = st.selectbox(
                    "Select an incident",
                    [
                        incident.get("incident_code")
                        for incident in filtered_incidents
                    ]
                )

                selected_incident = next(
                    incident for incident in filtered_incidents
                    if incident.get("incident_code") == selected_code
                )

                severity = selected_incident.get(
                    "severity", "UNKNOWN"
                )

                st.markdown(
                    f"### {selected_incident.get('title', 'Incident')}"
                )

                if severity == "CRITICAL":
                    st.error(f"Severity: {severity}")
                elif severity == "HIGH":
                    st.warning(f"Severity: {severity}")
                else:
                    st.info(f"Severity: {severity}")

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:

                    st.write(
                        f"**Incident ID:** "
                        f"{selected_incident.get('incident_code')}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{selected_incident.get('category')}"
                    )

                    st.write(
                        f"**Source file:** "
                        f"{selected_incident.get('filename')}"
                    )

                with detail_col2:

                    st.write(
                        f"**First seen:** "
                        f"{selected_incident.get('first_seen') or 'N/A'}"
                    )

                    st.write(
                        f"**Last seen:** "
                        f"{selected_incident.get('last_seen') or 'N/A'}"
                    )

                    st.write(
                        f"**Total events:** "
                        f"{selected_incident.get('event_count') or 'N/A'}"
                    )

                    st.write(
                        f"**Trigger events:** "
                        f"{selected_incident.get('trigger_count') or 'N/A'}"
                    )

                st.markdown("#### Correlation Explanation")

                correlation_reason = selected_incident.get(
                    "correlation_reason"
                )

                if correlation_reason:
                    st.info(correlation_reason)
                else:
                    st.caption(
                        "No correlation details available for this incident."
                    )

                # ----------------------------------
                # SAVED DIAGNOSIS STATUS
                # ----------------------------------

                st.markdown("#### AI Diagnosis Status")

                try:

                    diagnosis_response = get_incident_diagnosis(
                        selected_incident["id"]
                    )

                    diagnosis = diagnosis_response.get("diagnosis")

                    if diagnosis:
                        st.success("A saved AI diagnosis is available.")

                        st.write(
                            diagnosis.get(
                                "summary",
                                "Diagnosis summary unavailable."
                            )
                        )

                    else:
                        st.warning("No saved AI diagnosis found.")

                except RuntimeError:

                    st.warning(
                        "No saved AI diagnosis found for this incident."
                    )

            else:

                st.info("Select another severity to see incidents.")

    except Exception as error:

        st.error("Unable to load incidents from the backend.")
        st.exception(error)
    
# ==========================================
# AI DIAGNOSIS
# ==========================================

elif page == "AI Diagnosis":

    st.title("AI Incident Diagnosis")

    st.caption(
        "Generate intelligent incident analysis using the local AI agent."
    )

    st.divider()

    try:

        response = get_incidents(limit=100)
        incidents = response.get("data", [])

        if not incidents:

            st.info(
                "No incidents available. Analyze a log file first."
            )

        else:

            st.subheader("Select an Incident")

            selected_incident = st.selectbox(
                "Choose an incident",
                incidents,
                format_func=lambda incident: (
                    f"{incident.get('incident_code', 'INC')} - "
                    f"{incident.get('title', 'Unknown incident')} "
                    f"({incident.get('severity', 'UNKNOWN')})"
                )
            )

            incident_id = selected_incident["id"]

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Incident Severity",
                    selected_incident.get("severity", "UNKNOWN")
                )

            with col2:
                st.metric(
                    "Related Events",
                    selected_incident.get("event_count", 0)
                )

            st.divider()

            # ----------------------------------
            # LOAD SAVED OR GENERATE DIAGNOSIS
            # ----------------------------------

            diagnosis = None

            if (
                st.session_state.get("diagnosis_incident_id")
                == incident_id
            ):
                diagnosis = st.session_state.get("active_diagnosis")

            else:

                try:

                    diagnosis_response = get_incident_diagnosis(
                        incident_id
                    )

                    diagnosis = diagnosis_response.get("diagnosis")

                except RuntimeError:
                    diagnosis = None

            if st.button(
                "Generate AI Diagnosis",
                type="primary",
                use_container_width=True
            ):

                with st.spinner(
                    "AI agent is analyzing the incident..."
                ):

                    try:

                        diagnosis_response = diagnose_incident(
                            incident_id
                        )

                        diagnosis = diagnosis_response.get("diagnosis")

                        st.session_state["active_diagnosis"] = diagnosis
                        st.session_state["diagnosis_incident_id"] = incident_id

                        st.success(
                            "AI diagnosis generated successfully!"
                        )

                    except Exception as error:

                        st.error("Unable to generate AI diagnosis.")
                        st.exception(error)

                        diagnosis = None

            # ----------------------------------
            # DISPLAY DIAGNOSIS
            # ----------------------------------

            if diagnosis:

                st.divider()

                st.subheader("Incident Summary")

                st.info(
                    diagnosis.get(
                        "summary",
                        "No summary available."
                    )
                )

                # ----------------------------------
                # ROOT CAUSE HYPOTHESES
                # ----------------------------------

                st.subheader("Root Cause Hypotheses")

                root_causes = diagnosis.get("root_causes", [])

                if root_causes:

                    for index, cause in enumerate(root_causes, start=1):

                        with st.expander(
                            f"Hypothesis {index}",
                            expanded=True
                        ):

                            st.write(
                                cause.get(
                                    "hypothesis",
                                    "No hypothesis available."
                                )
                            )

                            confidence = cause.get("confidence", 0)

                            st.write(
                                f"Confidence: {confidence * 100:.1f}%"
                            )

                            st.progress(
                                max(0.0, min(float(confidence), 1.0))
                            )

                            st.markdown("**Supporting Evidence**")

                            evidence = cause.get("evidence", [])

                            if evidence:

                                for item in evidence:
                                    st.code(item)

                            else:

                                st.caption(
                                    "No direct evidence available."
                                )

                else:

                    st.warning(
                        "No root cause hypotheses were generated."
                    )

                # ----------------------------------
                # RECOMMENDATIONS
                # ----------------------------------

                st.subheader("Recommendations")

                recommendations = diagnosis.get(
                    "recommendations",
                    []
                )

                if recommendations:

                    for index, recommendation in enumerate(
                        recommendations,
                        start=1
                    ):

                        st.markdown(
                            f"**{index}.** {recommendation}"
                        )

                else:

                    st.info("No recommendations available.")

                # ----------------------------------
                # LIMITATIONS
                # ----------------------------------

                st.subheader("Analysis Limitations")

                limitations = diagnosis.get("limitations", [])

                if limitations:

                    for limitation in limitations:
                        st.warning(limitation)

                else:

                    st.caption(
                        "No limitations were reported."
                    )

            else:

                st.info(
                    "No saved diagnosis found. "
                    "Click Generate AI Diagnosis to start the analysis."
                )

    except Exception as error:

        st.error("Unable to load AI Diagnosis page.")
        st.exception(error)
    

elif page == "Reports":

    st.title("Reports & Analytics")

    st.markdown(
        "Analyze your log files, events, incidents and AI diagnoses."
    )

    try:
        # Fetch report data from FastAPI
        response = get_report_summary()
        report_data = response["data"]

        kpis = report_data["kpis"]
        log_levels = report_data["log_levels"]
        severities = report_data["severities"]
        categories = report_data["categories"]

        # ----------------------------------
        # KPI CARDS
        # ----------------------------------

        st.subheader("Overview")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Files",
            kpis["total_files"]
        )

        col2.metric(
            "Total Events",
            kpis["total_events"]
        )

        col3.metric(
            "Total Incidents",
            kpis["total_incidents"]
        )

        col4.metric(
            "AI Diagnoses",
            kpis["total_diagnoses"]
        )

        st.divider()

        # ----------------------------------
        # ERROR RATE
        # ----------------------------------

        st.subheader("Error Monitoring")

        error_col1, error_col2 = st.columns(2)

        error_col1.metric(
            "Error Rate",
            f'{kpis["error_rate"]:.2f}%'
        )

        error_col2.metric(
            "Error Events",
            kpis["error_events"]
        )

        st.caption(
            "Error Rate = (ERROR + CRITICAL events) / Total events."
        )

        st.divider()

        # ----------------------------------
        # LOG LEVEL CHART
        # ----------------------------------

        st.subheader("Log Levels Distribution")

        if log_levels:

            levels_df = pd.DataFrame(
                list(log_levels.items()),
                columns=["Log Level", "Count"]
            )

            fig_levels = px.bar(
                levels_df,
                x="Log Level",
                y="Count",
                color="Log Level",
                text="Count",
                title="Events by Log Level"
            )

            fig_levels.update_layout(
                template="plotly_dark",
                showlegend=False
            )

            st.plotly_chart(
                fig_levels,
                use_container_width=True
            )

        else:
            st.info("No log level data available.")

        st.divider()

        # ----------------------------------
        # INCIDENT CHARTS
        # ----------------------------------

        st.subheader("Incident Analytics")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:

            st.markdown("**Incident Severity**")

            if severities:

                severity_df = pd.DataFrame(
                    list(severities.items()),
                    columns=["Severity", "Count"]
                )

                fig_severity = px.pie(
                    severity_df,
                    names="Severity",
                    values="Count",
                    hole=0.45
                )

                fig_severity.update_layout(
                    template="plotly_dark"
                )

                st.plotly_chart(
                    fig_severity,
                    use_container_width=True
                )

            else:
                st.info("No severity data available.")

        with chart_col2:

            st.markdown("**Incident Categories**")

            if categories:

                category_df = pd.DataFrame(
                    list(categories.items()),
                    columns=["Category", "Count"]
                )

                fig_categories = px.bar(
                    category_df,
                    x="Category",
                    y="Count",
                    color="Category",
                    text="Count"
                )

                fig_categories.update_layout(
                    template="plotly_dark",
                    showlegend=False
                )

                st.plotly_chart(
                    fig_categories,
                    use_container_width=True
                )

            else:
                st.info("No category data available.")

        st.divider()

        # ----------------------------------
        # CSV EXPORT
        # ----------------------------------

        st.subheader("Export Reports")

        export_rows = []

        # KPI data
        for key, value in kpis.items():

            export_rows.append({
                "Section": "KPI",
                "Metric": key,
                "Value": value
            })

        # Log levels
        for key, value in log_levels.items():

            export_rows.append({
                "Section": "Log Levels",
                "Metric": key,
                "Value": value
            })

        # Severities
        for key, value in severities.items():

            export_rows.append({
                "Section": "Incident Severity",
                "Metric": key,
                "Value": value
            })

        # Categories
        for key, value in categories.items():

            export_rows.append({
                "Section": "Incident Categories",
                "Metric": key,
                "Value": value
            })

        export_df = pd.DataFrame(export_rows)

        csv_data = export_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="Download Reports (CSV)",
            data=csv_data,
            file_name="logmind_reports.csv",
            mime="text/csv"
        )

        st.success("Reports loaded successfully.")

    except Exception as error:

        st.error("Unable to load Reports Dashboard.")
        st.exception(error)
