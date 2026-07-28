from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.debug:
        from app.modules.registry import validate_resolution

        result = validate_resolution()
        if not result["resolution_ok"]:
            raise RuntimeError(f"Module registry failed: {result.get('errors', [])}")
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
