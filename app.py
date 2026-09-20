from fastapi import FastAPI

from api.routers.analysis import router as analysis_router
from api.routers.emails import router as emails_router
from models.api_models import HealthResponse

app = FastAPI(
    title="Jarvis Email Assistant API",
    description=(
        "Gmail retrieval, parsing and structured inbox intelligence."
    ),
    version="0.1.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="jarvis-email-assistant",
        version="0.1.0",
    )


app.include_router(emails_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")