"""Main application module for users service."""

import logging
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
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
    
    # Database initialization
    @app.on_event("startup")
    async def startup():
        logger.info("Initializing database...")
        db_settings = DatabaseSettings(
            url=settings.DATABASE_URL,
            echo=settings.DEBUG
        )
        db_client = initialize_db(db_settings)
        await db_client.create_tables()
        logger.info("Database initialized successfully")
    
    @app.on_event("shutdown")
    async def shutdown():
        from booking_db import get_db_client
        logger.info("Closing database connections...")
        await get_db_client().close()
        logger.info("Database connections closed")
    
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
