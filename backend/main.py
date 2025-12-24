"""
Quoted - Voice to Quote for Contractors
Main FastAPI application.
"""

import os
import logging
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .models.database import init_db
from .api import quotes, contractors, onboarding, auth, billing, pricing_brain, demo, referral, share, testimonials, learning, invoices, customers, tasks

# Configure logger
logger = logging.getLogger(__name__)

# Initialize Sentry if DSN is configured
if settings.sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=1.0,  # 100% of transactions for performance monitoring
            profiles_sample_rate=1.0,  # 100% of transactions for profiling
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
        logger.info(f"Sentry initialized for environment: {settings.environment}")
    except ImportError:
        logger.warning(
            "Sentry SDK not installed. "
            "Run: pip install sentry-sdk[fastapi]. "
            "Error tracking will not be available."
        )
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
else:
    logger.info("Sentry DSN not configured - error tracking disabled")


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

# CORS middleware with Railway preview environment support (DISC-077)
# allow_origin_regex enables Railway PR preview URLs: pr-{number}-quoted.up.railway.app
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.up\.railway\.app",  # Railway preview environments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(quotes.router, prefix="/api/quotes", tags=["Quotes"])
app.include_router(contractors.router, prefix="/api/contractors", tags=["Contractors"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["Onboarding"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(pricing_brain.router, prefix="/api/pricing-brain", tags=["Pricing Brain"])
app.include_router(demo.router, prefix="/api/demo", tags=["Demo"])
app.include_router(referral.router, prefix="/api/referral", tags=["Referral"])
app.include_router(share.router, prefix="/api/quotes", tags=["Share Quote"])
app.include_router(testimonials.router, prefix="/api/testimonials", tags=["Testimonials"])
app.include_router(learning.router, prefix="/api/learning", tags=["Learning"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])  # DISC-071
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])  # DISC-088
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])  # DISC-092


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
templates = Jinja2Templates(directory=str(frontend_path))

if frontend_path.exists():
    @app.get("/", response_class=HTMLResponse)
    async def serve_landing(request: Request):
        """Serve the landing page with injected config."""
        return templates.TemplateResponse("landing.html", {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "sentry_dsn": settings.sentry_dsn,
            "environment": settings.environment,
        })

    @app.get("/app", response_class=HTMLResponse)
    async def serve_app(request: Request):
        """Serve the main application with injected config."""
        return templates.TemplateResponse("index.html", {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "sentry_dsn": settings.sentry_dsn,
            "environment": settings.environment,
            "stripe_publishable_key": settings.stripe_publishable_key,
        })

    @app.get("/demo")
    async def serve_demo():
        """Serve the functional demo page - generate real quotes without signup."""
        return FileResponse(frontend_path / "try.html")

    @app.get("/try")
    async def serve_try():
        """Serve the functional demo page - generate real quotes without signup."""
        return FileResponse(frontend_path / "try.html")

    @app.get("/demo-promo")
    async def serve_demo_promo():
        """Redirect legacy demo-promo to /try."""
        return RedirectResponse("/try", status_code=301)

    @app.get("/terms")
    async def serve_terms():
        """Serve the Terms of Service page."""
        return FileResponse(frontend_path / "terms.html")

    @app.get("/privacy")
    async def serve_privacy():
        """Serve the Privacy Policy page."""
        return FileResponse(frontend_path / "privacy.html")

    @app.get("/use-cases")
    async def serve_use_cases():
        """Serve the Use Cases page - industry examples and demos."""
        return FileResponse(frontend_path / "use-cases.html")

    @app.get("/help", response_class=HTMLResponse)
    async def serve_help(request: Request):
        """Serve the Help & FAQ page with injected config."""
        return templates.TemplateResponse("help.html", {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "sentry_dsn": settings.sentry_dsn,
            "environment": settings.environment,
        })

    @app.get("/shared/{token}", response_class=HTMLResponse)
    async def serve_shared_quote(request: Request, token: str):
        """Serve the public shared quote view with injected config."""
        return templates.TemplateResponse("quote-view.html", {
            "request": request,
            "token": token,
            "posthog_api_key": settings.posthog_api_key,
            "sentry_dsn": settings.sentry_dsn,
            "environment": settings.environment,
        })

    @app.get("/for-customers", response_class=HTMLResponse)
    async def serve_customer_landing(request: Request):
        """Serve the customer landing page (viral growth from shared quotes)."""
        return templates.TemplateResponse("for-customers.html", {
            "request": request,
            "posthog_api_key": settings.posthog_api_key,
            "sentry_dsn": settings.sentry_dsn,
            "environment": settings.environment,
        })

    # Mount static files (CSS, JS, images if any)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
