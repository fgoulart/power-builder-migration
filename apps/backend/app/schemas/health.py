from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    environment: str


class ModuleStatusItem(BaseModel):
    id: str
    pbl: str
    status: str
    load_order: int = Field(ge=1)


class ModulesResponse(BaseModel):
    runtime_modules: list[ModuleStatusItem]
    build_only_modules: list[ModuleStatusItem]
    resolution_ok: bool
    errors: list[str] = Field(default_factory=list)
