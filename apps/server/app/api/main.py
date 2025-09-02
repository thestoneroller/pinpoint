from fastapi import APIRouter

from .routes import search

api_router = APIRouter()
api_router.include_router(search.router, tags=["Search"])
