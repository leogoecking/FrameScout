from datetime import datetime, timezone

from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.core.database import check_db_connection
from app.domain.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Healthcheck detalhado",
    description="Retorna status geral da API e conectividade com o banco de dados.",
)
async def get_health(response: Response) -> HealthResponse:
    db_ok = await check_db_connection()
    db_status = "connected" if db_ok else "disconnected"

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        service="api",
        environment=settings.ENVIRONMENT,
        version=settings.PROJECT_VERSION,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/health/live",
    summary="Liveness Probe",
    description="Indica que o processo da API está vivo.",
)
async def get_liveness() -> dict:
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get(
    "/health/ready",
    summary="Readiness Probe",
    description="Indica que a API e o banco de dados estão prontos para receber tráfego.",
)
async def get_readiness(response: Response) -> dict:
    db_ok = await check_db_connection()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unready", "database": "disconnected"}
    return {"status": "ready", "database": "connected"}
