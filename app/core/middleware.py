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
        # Allow preflight OPTIONS requests to reach CORSMiddleware
        if request.method == "OPTIONS":
            return await call_next(request)

        origin = request.headers.get("origin")
        if origin and not self._is_allowed(origin):
            return JSONResponse(ApiResponse.error("Origin not allowed").model_dump(), status_code=403)
        return await call_next(request)

    def _is_allowed(self, origin: str) -> bool:
        if origin in self._allowed:
            return True
        # Automatically allow all Vercel deployment URLs (*.vercel.app)
        if origin.endswith(".vercel.app"):
            return True
        return False
