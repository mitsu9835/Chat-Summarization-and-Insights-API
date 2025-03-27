"""
Main FastAPI application entry point.
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from api.routes import chat, user, summary
from api.middleware import LoggingMiddleware, RateLimitingMiddleware
from db.mongodb import MongoDB
from config.settings import settings
from config.logging import logger


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for chat summarization and insights using LLM",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_per_minute=60)

# Include routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(summary.router, prefix=settings.API_V1_STR)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )


@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on application startup."""
    await MongoDB.connect_to_database()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on application shutdown."""
    await MongoDB.close_database_connection()


@app.get("/", tags=["status"])
async def root():
    """Root endpoint for API status check."""
    return {"status": "online", "message": "Chat Summarization API is running"}


@app.get("/health", tags=["status"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        await MongoDB.db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected"}
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)