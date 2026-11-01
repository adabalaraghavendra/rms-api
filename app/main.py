from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_client, ping
from app.core.error_handlers import register_exception_handlers
from app.core.middleware import OriginGuardMiddleware
from app.routers import api_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ping()  # fail fast, with a clear error, if MongoDB cannot be reached
    yield
    close_client()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Room Management API", version="2.0.0", lifespan=lifespan)

    # 1) CORS: tells browsers which site may call this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.client_origins),
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    # 2) Origin guard: the server itself refuses browser calls from other sites.
    #    Added after CORS so it runs first.
    app.add_middleware(OriginGuardMiddleware, allowed_origins=settings.client_origins)

    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["Health"])
    def health():
        return {"Server ": "Running", "Database": "Connected"}

    return app


app = create_app()
