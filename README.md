\# LogMind AI — Intelligent Log Analysis \& Incident Diagnosis



LogMind AI is a local AI-powered log analysis platform designed to transform raw application logs into structured events, detect anomalies, correlate related errors into incidents, and generate AI-assisted incident diagnoses.



The platform combines rule-based detection, machine learning, incident correlation, and a locally hosted Large Language Model (LLM) to help users understand system failures and investigate potential root causes.



\## Key Features



\- \*\*Log Ingestion:\*\* Upload and analyze `.log`, `.txt`, and `.csv` files.

\- \*\*Log Parsing:\*\* Extract timestamps, log levels, and messages from raw log lines.

\- \*\*Error Detection:\*\* Identify and classify errors using deterministic detection rules.

\- \*\*Anomaly Detection:\*\* Extract numerical features and apply a machine learning baseline.

\- \*\*Incident Correlation:\*\* Group related log events into meaningful incidents.

\- \*\*AI Diagnosis:\*\* Generate incident summaries, root-cause hypotheses, supporting evidence, recommendations, and limitations.

\- \*\*Evidence Validation:\*\* Verify that AI-provided evidence matches original log messages.

\- \*\*Interactive Dashboard:\*\* Explore logs, incidents, diagnoses, and analysis statistics.

\- \*\*Reports \& Export:\*\* Visualize KPIs and distributions and export report data as CSV.

\- \*\*Local Execution:\*\* Run the application locally without paid external AI APIs.



\## Architecture



```text

&#x20;                ┌──────────────────────┐

&#x20;                │    Streamlit UI      │

&#x20;                │  Dashboard \& Reports│

&#x20;                └──────────┬───────────┘

&#x20;                           │ HTTP Requests

&#x20;                           ▼

&#x20;                ┌──────────────────────┐

&#x20;                │     FastAPI API      │

&#x20;                │  Log Analysis Routes │

&#x20;                └──────────┬───────────┘

&#x20;                           │

&#x20;            ┌──────────────┼──────────────┐

&#x20;            ▼              ▼              ▼

&#x20;      ┌──────────┐  ┌────────────┐  ┌────────────┐

&#x20;      │ Ingestion│  │ Detection  │  │ Correlation│

&#x20;      │ \& Parsing│  │ \& ML       │  │  Engine    │

&#x20;      └──────────┘  └────────────┘  └────────────┘

&#x20;            │              │              │

&#x20;            └──────────────┼──────────────┘

&#x20;                           ▼

&#x20;                   ┌──────────────┐

&#x20;                   │   SQLite DB  │

&#x20;                   └──────────────┘

&#x20;                           │

&#x20;                           ▼

&#x20;                   ┌──────────────┐

&#x20;                   │  AI Agent    │

&#x20;                   │ Ollama + Qwen│

&#x20;                   └──────────────┘

```



\## Technology Stack



| Component | Technologies |

|---|---|

| Backend | Python, FastAPI, Uvicorn |

| Frontend | Streamlit |

| Data Processing | Pandas, NumPy |

| Machine Learning | Scikit-learn |

| Data Visualization | Plotly |

| Database | SQLite |

| Local LLM Runtime | Ollama |

| AI Model | Qwen2.5:1.5B |

| Testing | Pytest, HTTPX |



\## Project Structure



```text

LogMindAI/

│

├── backend/

│   ├── api/

│   │   └── routes\_logs.py

│   ├── core/

│   │   └── database.py

│   ├── services/

│   │   ├── ai\_agent.py

│   │   ├── analysis\_pipeline.py

│   │   ├── anomaly\_detector.py

│   │   ├── correlator.py

│   │   ├── dataset\_builder.py

│   │   ├── detector.py

│   │   ├── feature\_extractor.py

│   │   ├── ingestion.py

│   │   ├── parser.py

│   │   └── synthetic\_data.py

│   └── main.py

│

├── frontend/

│   ├── app.py

│   ├── api\_client.py

│   └── config.py

│

├── tests/

├── data/

├── reports/

├── docs/

├── requirements.txt

└── README.md

```



\## Prerequisites



\- Python 3.11+

\- Git

\- Ollama

\- Qwen2.5:1.5B model



\## Installation



\### 1. Clone the repository



```bash

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd LogMindAI

```



\### 2. Create a virtual environment



Windows PowerShell:



```powershell

python -m venv .venv

.venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

python -m pip install -r requirements.txt

```



\### 4. Install and configure Ollama



Install Ollama from:



https://ollama.com/



Download the model:



```powershell

ollama pull qwen2.5:1.5b

```



Make sure Ollama is running locally.



\## Running the Application



The application requires two terminals.



\### Terminal 1 — Start the FastAPI backend



```powershell

uvicorn backend.main:app --reload

```



Backend:



http://127.0.0.1:8000



API documentation:



http://127.0.0.1:8000/docs



Health check:



http://127.0.0.1:8000/api/v1/health



\### Terminal 2 — Start the Streamlit frontend



Activate the virtual environment if necessary, then run:



```powershell

python -m streamlit run frontend/app.py

```



Streamlit will display the local application URL in the terminal.



\## Application Modules



| Module | Description |

|---|---|

| Dashboard | Overview of analyzed logs and incidents |

| Log Analyzer | Upload and analyze log files |

| Incident Explorer | Browse and filter detected incidents |

| AI Diagnosis | Generate and inspect AI-assisted diagnoses |

| Reports | Explore statistics, charts, and CSV exports |



\## AI Diagnosis Workflow



1\. Retrieve incident information and associated log events.

2\. Prepare relevant incident data for the AI agent.

3\. Send the incident context to the local Qwen2.5:1.5B model through Ollama.

4\. Generate a structured diagnosis containing:

&#x20;  - Incident summary

&#x20;  - Root-cause hypotheses

&#x20;  - Supporting log evidence

&#x20;  - Confidence scores

&#x20;  - Recommendations

&#x20;  - Diagnostic limitations

5\. Validate the returned JSON structure and evidence against original log messages.

6\. Save and display the diagnosis.



\*\*Important:\*\* AI-generated root causes are hypotheses, not confirmed facts. Confidence scores are model-generated estimates and are not calibrated probabilities. Human review is required before taking operational action.



\## Testing



Run the automated test suite:



```powershell

python -m pytest -v

```



Check Python dependency consistency:



```powershell

python -m pip check

```



\## Security \& Limitations



\- Log files are treated as untrusted input.

\- Uploaded files are subject to application validation and size limits.

\- AI evidence is checked against original log messages.

\- AI diagnoses may be incomplete or incorrect and require human verification.

\- The application does not automatically execute remediation actions.

\- The current setup is designed for local development and demonstration.



\## Future Improvements



\- Advanced anomaly detection and model evaluation.

\- More robust log format support.

\- Improved incident correlation.

\- Expanded reporting and monitoring capabilities.

\- Additional local LLM model comparisons.

\- Deployment and production-readiness improvements.



\## Author



Developed as a Data Engineering and Artificial Intelligence project.



\---



\*\*LogMind AI — From Raw Logs to Actionable Insights.\*\*

