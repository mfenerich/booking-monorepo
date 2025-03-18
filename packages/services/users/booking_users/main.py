"""Main application module for users service."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from booking_db import DatabaseSettings, initialize_db
from booking_api import configure_exception_handlers

from .config import settings
from .routers import router as users_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("booking_users")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI."""
    # Startup
    logger.info("Initializing database...")
    db_settings = DatabaseSettings(
        url=settings.DATABASE_URL,
        echo=settings.DEBUG
    )
    db_client = initialize_db(db_settings)
    await db_client.create_tables()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    from booking_db import get_db_client
    logger.info("Closing database connections...")
    await get_db_client().close()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app with explicitly set docs URL (not using API prefix)
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        # Set docs URL explicitly to root level
        docs_url="/docs",  
        redoc_url="/redoc"
    )
    
    # Configure exception handlers
    app = configure_exception_handlers(app)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(users_router, prefix=settings.API_PREFIX)

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Booking Users Service",
            "docs": "/docs",
            "api_prefix": settings.API_PREFIX,
            "endpoints": [
                f"{settings.API_PREFIX}/users/register"
            ]
        }
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "booking_users.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
