from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import CLIENT_ORIGINS
from app.core.database import pool
from app.routers import auth, expenses, rent, summary, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    pool.open()
    yield
    pool.close()


app = FastAPI(title="Room Management API", lifespan=lifespan)

# 1) CORS: tells browsers which site may call this API (origins come from CLIENT_ORIGIN in .env).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CLIENT_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# 2) Origin guard: the server itself refuses browser calls from any other site.
#    Added after CORS so it runs first (outermost). Calls with no Origin header
#    (curl, Postman, server-to-server) pass here and are still protected by login tokens.
@app.middleware("http")
async def only_allowed_origins(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin not in CLIENT_ORIGINS:
        return JSONResponse({"message": "Origin not allowed"}, status_code=499)
    return await call_next(request)


# The React client reads errors from a `message` field
@app.exception_handler(HTTPException)
async def http_error(_req: Request, exc: HTTPException):
    return JSONResponse({"message": exc.detail}, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error(_req: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(p) for p in first["loc"] if p != "body")
    return JSONResponse({"message": f"Invalid {field}: {first['msg']}"}, status_code=400)


@app.get("/health")
def health():
    return {"ok": True}


for module in (auth, users, expenses, rent, summary):
    app.include_router(module.router, prefix="/api")
