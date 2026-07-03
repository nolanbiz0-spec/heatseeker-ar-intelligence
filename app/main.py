from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .database import init_db, close_db
from .api import artists, intelligence


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Heatseeker A&R Intelligence",
    description="Artist discovery and momentum tracking for record label A&R",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(artists.router, prefix="/api/artists", tags=["artists"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["intelligence"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "operational",
        "service": "Heatseeker A&R Intelligence",
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    # TODO: Add database and Redis connectivity checks
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "apis": {
            "spotify": "configured",
            "youtube": "configured", 
            "lastfm": "configured",
            "musicbrainz": "configured"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )