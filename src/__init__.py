from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.auth.auth_routes import auth_router
from src.books.book_routes import book_router
from src.config import settings
from src.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Bookly API",
        description="A complete REST API for user authentication and book management with JWT authentication.",
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/", tags=["root"], summary="API Root")
    async def root():
        return {
            "message": "Welcome to Bookly API",
            "version": settings.VERSION,
            "docs": "/docs",
        }

    # Register routers
    app.include_router(auth_router)
    app.include_router(book_router)

    return app


app = create_app()
