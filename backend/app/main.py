from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.logging_config import setup_logging
from app.routers import users, venues, interests, recommendations, reservations

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting", extra={"app_env": settings.APP_ENV})
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Luna Take Home API",
    description="Backend API for Luna social venue discovery platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific iOS app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
        },
    )

    try:
        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        return response

    except Exception as e:
        # Log error without leaking stack trace in production
        logger.error(
            f"Request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e) if settings.APP_ENV == "local" else "Internal server error",
            },
        )

        # Return generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


# Include routers
app.include_router(users.router)
app.include_router(venues.router)
app.include_router(interests.router)
app.include_router(recommendations.router)
app.include_router(reservations.router)


@app.get("/")
def root():
    return {
        "message": "Luna Take Home API",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
