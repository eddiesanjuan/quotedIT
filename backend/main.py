"""
Quoted - Voice to Quote for Contractors
Main FastAPI application.
"""

import os
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import settings
from .models.database import init_db
from .api import quotes, contractors, onboarding, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")

    # Ensure data directories exist
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/uploads", exist_ok=True)
    os.makedirs("./data/pdfs", exist_ok=True)

    # Initialize database
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")


# Create application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Voice-to-Quote generation for contractors. Speak your estimate, get a professional quote.",
    lifespan=lifespan,
)

# CORS middleware (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["Quotes"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["Contractors"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])


@app.get("/api/info")
async def api_info():
    """API info endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML."""
        return FileResponse(frontend_path / "index.html")

    # Mount static files (CSS, JS, images if any)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
