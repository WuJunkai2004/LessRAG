from fastapi import APIRouter

from server.schema.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(success=True, message="Service is healthy")
