"""
Quoted - Voice to Quote for Contractors
Main FastAPI application.
"""

import os
import logging
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .models.database import init_db
from .services.logging import configure_logging, get_logger

# Configure structured logging (INFRA-008)
configure_logging(
    environment=settings.environment,
    log_level="DEBUG" if settings.debug else "INFO"
)
logger = get_logger("quoted.main")

from .api import quotes, contractors, onboarding, auth, billing, pricing_brain, demo, referral, share, testimonials, learning, invoices, customers, tasks, followup

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


# Rate limiter with enhanced configuration (SEC-004)
from .services.rate_limiting import (
    ip_limiter,
    rate_limit_exceeded_handler,
)
limiter = ip_limiter  # Use IP-based limiter as default


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
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        extra={"environment": settings.environment}
    )

    # Ensure data directories exist
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/uploads", exist_ok=True)
    os.makedirs("./data/pdfs", exist_ok=True)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Start background scheduler (Wave 3)
    # SECURITY FIX (P0-02): Only start scheduler in ONE worker to prevent duplicate jobs
    # With --workers 4, each worker runs lifespan, so we use an env var guard
    from .services.scheduler import start_scheduler, stop_scheduler
    scheduler_started = False
    if os.environ.get("SCHEDULER_STARTED") != "1":
        os.environ["SCHEDULER_STARTED"] = "1"
        start_scheduler()
        scheduler_started = True
        logger.info("Scheduler started (this worker is the scheduler leader)")
    else:
        logger.info("Scheduler skipped (another worker is the scheduler leader)")

    yield

    # Shutdown
    logger.info("Shutting down...")
    if scheduler_started:
        stop_scheduler()


# Create application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Voice-to-Quote generation for contractors. Speak your estimate, get a professional quote.",
    lifespan=lifespan,
)

# Add rate limiter to app state with custom handler (SEC-004)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

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
# allow_origin_regex restricted to Quoted's Railway domains only (pr-XXX-quoted and web-production-*)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://(pr-\d+-quoted|web-production-\w+)\.up\.railway\.app",  # Only Quoted's Railway domains
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
app.include_router(followup.router, prefix="/api/followup", tags=["Follow-Up"])  # INNOV-3


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
    """Quick health check for load balancers."""
    from .services.health import get_quick_health
    return await get_quick_health()


@app.get("/health/full")
@limiter.limit("2/minute")  # SECURITY FIX (P0-08): Rate limit to prevent API cost burn attacks
async def health_full(request: Request):
    """Comprehensive health check including all external services.

    Rate limited to 2/minute to prevent abuse (external API calls cost money).
    """
    from .services.health import check_all_health
    return await check_all_health(include_external=True)


@app.get("/health/scheduler")
async def health_scheduler():
    """Health check for background scheduler (Wave 3)."""
    from .services.health import get_scheduler_health
    return get_scheduler_health()


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

    @app.get("/invoice/{token}", response_class=HTMLResponse)
    async def serve_shared_invoice(request: Request, token: str):
        """Serve the public shared invoice view with injected config."""
        return templates.TemplateResponse("invoice-view.html", {
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

    # SEO: Sitemap and robots.txt
    @app.get("/sitemap.xml")
    async def serve_sitemap():
        """Serve the XML sitemap for search engines."""
        return FileResponse(frontend_path / "sitemap.xml", media_type="application/xml")

    @app.get("/robots.txt")
    async def serve_robots():
        """Serve robots.txt for search engine crawlers."""
        return FileResponse(frontend_path / "robots.txt", media_type="text/plain")

    # Blog routes
    @app.get("/blog/")
    @app.get("/blog")
    async def serve_blog_index():
        """Serve the blog index page."""
        return FileResponse(frontend_path / "blog" / "index.html")

    @app.get("/blog/{filename}")
    async def serve_blog_post(filename: str):
        """Serve individual blog posts."""
        blog_path = frontend_path / "blog" / filename
        if blog_path.exists() and blog_path.suffix == ".html":
            return FileResponse(blog_path)
        raise HTTPException(status_code=404, detail="Blog post not found")

    # Mount static files (CSS, JS, images if any)
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
