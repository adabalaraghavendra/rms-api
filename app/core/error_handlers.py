"""Turn every error into the standard envelope: {status, message, data, pagination}."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.shared.response import ApiResponse

logger = logging.getLogger("rms")


def _error(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(ApiResponse.error(message).model_dump(), status_code=status_code)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error(_req: Request, exc: AppError):
        return _error(exc.message, exc.status_code)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_req: Request, exc: StarletteHTTPException):
        return _error(str(exc.detail), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_req: Request, exc: RequestValidationError):
        first = exc.errors()[0]
        field = ".".join(str(p) for p in first["loc"] if p not in ("body", "query"))
        return _error(f"Invalid {field}: {first['msg']}", 400)

    @app.exception_handler(PyMongoError)
    async def database_error(_req: Request, exc: PyMongoError):
        logger.exception("Database error", exc_info=exc)
        return _error("Database unavailable, please try again shortly", 503)

    @app.exception_handler(Exception)
    async def unexpected_error(_req: Request, exc: Exception):
        logger.exception("Unhandled error", exc_info=exc)
        return _error("Internal server error", 500)
