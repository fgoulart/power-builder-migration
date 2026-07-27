from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
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

# PBBV-2 BA Gate A (remediation-94): docs/pbbv-2-jira-specification.md applied as BA deliverable; /api/v1/psr/* stays deferred. I'll inspect the destination repo and card config, then produce a complete Jira specification that follows all gates.
