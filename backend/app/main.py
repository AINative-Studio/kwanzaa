"""Kwanzaa FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.v1.endpoints import search
from app.core.config import settings
from app.core.errors import (
    APIError,
    api_error_handler,
    generic_exception_handler,
    http_exception_handler,
    validation_error_handler,
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    Kwanzaa Semantic Search API

    This API provides semantic search capabilities across the Kwanzaa corpus
    with comprehensive provenance filtering and persona-driven query support.

    Key Features:
    - Semantic vector search with natural language queries
    - Provenance-first metadata filtering
    - Persona-driven search configurations
    - Citation tracking and source attribution
    - Transparent search execution metadata

    For more information, visit: https://github.com/AINative-Studio/kwanzaa
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(
    search.router,
    prefix=f"{settings.API_V1_PREFIX}/search",
    tags=["search"],
)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint.

    Returns:
        API information
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
