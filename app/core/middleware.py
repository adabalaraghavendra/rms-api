from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.shared.response import ApiResponse


class OriginGuardMiddleware(BaseHTTPMiddleware):
    """Refuse browser calls from any site that is not in CLIENT_ORIGIN.

    Requests without an Origin header (curl, Postman, server-to-server) pass
    through; they are still protected by login tokens.
    """

    def __init__(self, app, allowed_origins):
        super().__init__(app)
        self._allowed = set(allowed_origins)

    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin")
        if origin and origin not in self._allowed:
            return JSONResponse(ApiResponse.error("Origin not allowed").model_dump(), status_code=403)
        return await call_next(request)
