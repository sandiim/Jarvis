from pydantic import BaseModel, Field


class InboxAnalysisRequest(BaseModel):
    max_results: int = Field(default=5, ge=1, le=50)
    query: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str