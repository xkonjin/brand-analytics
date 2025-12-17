# =============================================================================
# FastAPI Application Entry Point
# =============================================================================
# This is the main entry point for the Brand Analytics API.
# It configures the FastAPI application, middleware, and routes.
# =============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import analysis, reports, health
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    
    This context manager handles:
    - Database connection pool initialization on startup
    - Playwright browser initialization (if needed)
    - Graceful shutdown of connections
    """
    # ---------------------------------------------------------------------
    # Startup: Initialize resources
    # ---------------------------------------------------------------------
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    
    # Initialize database connection pool
    await init_db()
    print("✅ Database connection pool initialized")
    
    # Yield control to the application
    yield
    
    # ---------------------------------------------------------------------
    # Shutdown: Clean up resources
    # ---------------------------------------------------------------------
    print("🛑 Shutting down application...")
    
    # Close database connections
    await close_db()
    print("✅ Database connections closed")


# =============================================================================
# Create FastAPI Application
# =============================================================================
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Brand Analytics API
    
    A comprehensive brand analysis tool that provides professional marketing audits
    across multiple dimensions:
    
    - **SEO Performance**: PageSpeed, meta tags, indexing
    - **Social Media**: Follower counts, engagement rates, platform presence
    - **Brand Messaging**: Archetype identification, tone analysis, readability
    - **Website UX**: CTAs, navigation, trust signals
    - **AI Discoverability**: Wikipedia, Knowledge Graph, structured data
    - **Content Analysis**: Recent posts, sentiment, content mix
    - **Team Presence**: LinkedIn, founder visibility
    - **Channel Fit**: Platform suitability scoring
    
    ### Getting Started
    
    1. POST `/api/v1/analyze` with a website URL to start analysis
    2. Poll `/api/v1/analysis/{id}` for progress updates
    3. GET `/api/v1/analysis/{id}/report` for the full report
    4. GET `/api/v1/analysis/{id}/pdf` to download PDF
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# =============================================================================
# Configure CORS Middleware
# =============================================================================
# Allow frontend applications to make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Register API Routes
# =============================================================================
# All routes are prefixed with /api/v1 for versioning
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"]
)

app.include_router(
    analysis.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Analysis"]
)

app.include_router(
    reports.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Reports"]
)


# =============================================================================
# Root Endpoint
# =============================================================================
@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint that provides basic API information.
    Redirects users to the API documentation.
    """
    return JSONResponse(
        content={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": f"{settings.API_V1_PREFIX}/health",
        }
    )


# =============================================================================
# Exception Handlers
# =============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    
    In production, this prevents stack traces from leaking to clients.
    In development, it provides more detailed error information.
    """
    if settings.DEBUG:
        # In debug mode, include exception details
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "type": type(exc).__name__,
            }
        )
    else:
        # In production, hide implementation details
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred. Please try again later.",
            }
        )


# =============================================================================
# Development Server Entry Point
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    
    # Run the development server
    # For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )

