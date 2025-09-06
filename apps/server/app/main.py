import instructor
from fastapi import FastAPI
from .core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from .api import api_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm = instructor.from_provider(
        "google/gemini-2.5-flash-lite",
        api_key=settings.GOOGLE_API_KEY,
        async_client=True,
    )
    yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
