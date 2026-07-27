from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str



class ModuleInfo(BaseModel):
    id: str
    pbl: str
    status: str
    load_order: int


class ModulesResponse(BaseModel):
    runtime_modules: list[ModuleInfo]
    build_only_modules: list[ModuleInfo]
    resolution_ok: bool
    errors: list[str]
