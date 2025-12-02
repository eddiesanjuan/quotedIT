"""
Quoted - Voice to Quote for Contractors
Main FastAPI application.
"""

import os
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .models.database import init_db
from .api import quotes, contractors, onboarding, auth, issues


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production."""

    async def dispatch(self, request: Request, call_next):
        # Check if behind a proxy (Railway sets X-Forwarded-Proto)
        forwarded_proto = request.headers.get("x-forwarded-proto", "")

        # Only redirect if in production and coming via HTTP
        if (settings.environment == "production" and
            forwarded_proto == "http" and
            request.url.path not in ["/health", "/api/info"]):
            # Build HTTPS URL
            https_url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(https_url, status_code=301)

        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler - startup and shutdown."""
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")

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

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# HTTPS redirect middleware (production only)
if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://quoted.it.com",
    "https://www.quoted.it.com",
    "https://web-production-0550.up.railway.app",
]

# In development, also allow localhost
if settings.environment != "production":
    ALLOWED_ORIGINS.extend([
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["Quotes"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["Contractors"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(issues.router, prefix="/api/issues", tags=["Issues"])


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
    async def serve_landing():
        """Serve the landing page."""
        return FileResponse(frontend_path / "landing.html")

    @app.get("/app")
    async def serve_app():
        """Serve the main application."""
        return FileResponse(frontend_path / "index.html")

    @app.get("/terms")
    async def serve_terms():
        """Serve the Terms of Service page."""
        return FileResponse(frontend_path / "terms.html")

    @app.get("/privacy")
    async def serve_privacy():
        """Serve the Privacy Policy page."""
        return FileResponse(frontend_path / "privacy.html")

    # Mount static files (CSS, JS, images if any)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
