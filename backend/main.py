
from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.core.database import initialize_database
from backend.api.routes_logs import router as logs_router
from backend.services.analysis_pipeline import create_baseline_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    initialize_database()
    print("Database initialized successfully!")

    print("Training ML baseline model...")
    app.state.ml_model = create_baseline_model()
    print("ML model loaded successfully!")

    yield

    print("LogMind AI shutting down...")


app = FastAPI(
    title="LogMind AI API",
    description="Intelligent Log Analysis and Incident Detection",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "application": "LogMind AI",
        "message": "Welcome to LogMind AI API",
        "version": "1.0.0"
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LogMind AI Backend"
    }


app.include_router(logs_router)
