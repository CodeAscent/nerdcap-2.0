"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.models import models  # ensure models are registered
from app.routers import auth, proposals, dashboard, recommendations, predictions, users
from app.stubs import get_all_stubs_status

settings = get_settings()

# Create DB tables (use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "Ooumph Agentic AI Ecosystem — AI-Enabled Land Allocation for Renewable Energy Projects in Andhra Pradesh. "
        "Built for the IndiaAI Innovation Challenge (AIKOSHI) by NREDCAP."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  # Allows all origins including production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Routers
app.include_router(auth.router)
app.include_router(proposals.router)
app.include_router(dashboard.router)
app.include_router(recommendations.router)
app.include_router(predictions.router)
app.include_router(users.router)


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "version": settings.version,
        "environment": settings.environment,
        "app": settings.app_name,
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "ai_agents": "healthy",
        }
    }


@app.get("/api/stubs/status", tags=["System"])
def stubs_status():
    return get_all_stubs_status()
