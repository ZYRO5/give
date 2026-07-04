from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database.session import init_db, get_db
from app.api import users, campaigns, donations, donors, reports
import logging

settings = get_settings()

# Setup logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Comprehensive Donor Management Platform API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(campaigns.router)
app.include_router(donations.router)
app.include_router(donors.router)
app.include_router(reports.router)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    logger.info("Database initialized")


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs"
    }


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment
    }


# API info
@app.get("/api/info")
async def api_info():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "users": "/api/v1/users",
            "campaigns": "/api/v1/campaigns",
            "donations": "/api/v1/donations",
            "donors": "/api/v1/donors",
            "reports": "/api/v1/reports"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
