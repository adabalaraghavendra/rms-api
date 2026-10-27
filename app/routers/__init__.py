"""HTTP endpoints, one module per feature. Routers only declare paths and
dependencies; the work happens in controllers -> services -> repositories."""
from fastapi import APIRouter

from app.routers import auth, expenses, rent, summary, users

api_router = APIRouter()
for _module in (auth, users, expenses, rent, summary):
    api_router.include_router(_module.router)
