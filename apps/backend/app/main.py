import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings, validate_runtime_resolution

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment == "development" or settings.debug:
        report = validate_runtime_resolution()
        if report.ok:
            logger.info("Runtime module registry resolution_ok=true (%s modules)", 10)
        else:
            logger.warning("Runtime module registry resolution failed: %s", report.errors)
    yield


app = FastAPI(
    title="Power Builder API",
    description="Backend API do monorepo Power Builder Migration",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix=settings.api_v1_prefix, tags=["v1"])


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Power Builder API", "docs": "/docs"}
