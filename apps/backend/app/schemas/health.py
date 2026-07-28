from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    environment: str


class ModuleInfo(BaseModel):
    id: str
    pbl: str
    status: str
    load_order: int = Field(ge=1)


class ModulesResponse(BaseModel):
    runtime_modules: list[ModuleInfo]
    build_only_modules: list[ModuleInfo]
    resolution_ok: bool
    errors: list[str] = Field(default_factory=list)
