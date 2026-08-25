from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.schemas import MediaCandidateRead
from app.services.media_service import MediaService

router = APIRouter(tags=["Media Candidates"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post(
    "/queries/{query_id}/search",
    response_model=List[MediaCandidateRead],
    status_code=status.HTTP_201_CREATED,
    summary="Buscar candidatos de mídia para uma query (Pexels / Wikimedia)",
)
async def search_query_media(
    query_id: UUID,
    db: DbSession,
    provider: Optional[str] = Query(
        default=None, description="Filtrar provedor ('pexels' ou 'wikimedia')"
    ),
    limit: int = Query(default=8, ge=1, le=50),
) -> List[MediaCandidateRead]:
    try:
        candidates = await MediaService.search_for_query(
            db, query_id, provider_name=provider, limit=limit
        )
        return [MediaCandidateRead.model_validate(c) for c in candidates]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/queries/{query_id}/candidates",
    response_model=List[MediaCandidateRead],
    summary="Listar candidatos de mídia já encontrados para uma query",
)
async def list_query_candidates(
    query_id: UUID,
    db: DbSession,
) -> List[MediaCandidateRead]:
    candidates = await MediaService.list_by_query(db, query_id)
    return [MediaCandidateRead.model_validate(c) for c in candidates]


@router.post(
    "/scenes/{scene_id}/search",
    response_model=List[MediaCandidateRead],
    status_code=status.HTTP_201_CREATED,
    summary="Buscar mídia para todas as queries de uma cena (Multi-Provider)",
)
async def search_scene_media(
    scene_id: UUID,
    db: DbSession,
    provider: Optional[str] = Query(
        default=None, description="Filtrar provedor ('pexels' ou 'wikimedia')"
    ),
    limit_per_query: int = Query(default=4, ge=1, le=20),
) -> List[MediaCandidateRead]:
    try:
        candidates = await MediaService.search_for_scene(
            db, scene_id, provider_name=provider, limit_per_query=limit_per_query
        )
        return [MediaCandidateRead.model_validate(c) for c in candidates]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/scenes/{scene_id}/candidates",
    response_model=List[MediaCandidateRead],
    summary="Listar todos os candidatos de mídia encontrados para uma cena",
)
async def list_scene_candidates(
    scene_id: UUID,
    db: DbSession,
) -> List[MediaCandidateRead]:
    candidates = await MediaService.list_by_scene(db, scene_id)
    return [MediaCandidateRead.model_validate(c) for c in candidates]


@router.get(
    "/candidates/{candidate_id}",
    response_model=MediaCandidateRead,
    summary="Obter detalhes de um candidato de mídia específico",
)
async def get_candidate(
    candidate_id: UUID,
    db: DbSession,
) -> MediaCandidateRead:
    candidate = await MediaService.get(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidato de mídia não encontrado",
        )
    return MediaCandidateRead.model_validate(candidate)


@router.post(
    "/scenes/{scene_id}/rerank",
    response_model=List[MediaCandidateRead],
    summary="Recalcular o Fidelity Score e reordenar candidatos da cena",
)
async def rerank_scene_candidates(
    scene_id: UUID,
    db: DbSession,
) -> List[MediaCandidateRead]:
    try:
        candidates = await MediaService.rerank_scene_candidates(db, scene_id)
        return [MediaCandidateRead.model_validate(c) for c in candidates]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e


@router.get(
    "/projects/{project_id}/fidelity-metrics",
    summary="Obter métricas consolidadas de fidelidade visual do projeto",
)
async def get_project_fidelity_metrics(
    project_id: UUID,
    db: DbSession,
):
    try:
        return await MediaService.get_project_fidelity_metrics(db, project_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e
