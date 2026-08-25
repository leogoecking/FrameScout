from typing import Annotated, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.schemas import (
    SearchQueryCreate,
    SearchQueryRead,
    SearchQueryUpdate,
)
from app.services.query_service import QueryService

router = APIRouter(tags=["Search Queries"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


# --- Scene-Scoped Query Endpoints ---


@router.post(
    "/scenes/{scene_id}/queries/generate",
    response_model=List[SearchQueryRead],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar queries automaticamente para uma cena",
)
async def generate_scene_queries(
    scene_id: UUID,
    db: DbSession,
) -> List[SearchQueryRead]:
    try:
        queries = await QueryService.generate_for_scene(db, scene_id)
        return [SearchQueryRead.model_validate(q) for q in queries]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post(
    "/projects/{project_id}/queries/generate",
    response_model=Dict[str, int],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar queries em lote para todas as cenas do projeto",
)
async def generate_project_queries(
    project_id: UUID,
    db: DbSession,
) -> Dict[str, int]:
    try:
        return await QueryService.generate_for_project(db, project_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/scenes/{scene_id}/queries",
    response_model=List[SearchQueryRead],
    summary="Listar queries de busca de uma cena",
)
async def list_scene_queries(
    scene_id: UUID,
    db: DbSession,
) -> List[SearchQueryRead]:
    queries = await QueryService.list_by_scene(db, scene_id)
    return [SearchQueryRead.model_validate(q) for q in queries]


@router.post(
    "/scenes/{scene_id}/queries",
    response_model=SearchQueryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar query de busca manualmente para uma cena",
)
async def create_scene_query(
    scene_id: UUID,
    data: SearchQueryCreate,
    db: DbSession,
) -> SearchQueryRead:
    try:
        created = await QueryService.create(db, scene_id, data)
        return SearchQueryRead.model_validate(created)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# --- Individual Query Endpoints ---


@router.get(
    "/queries/{query_id}",
    response_model=SearchQueryRead,
    summary="Obter detalhes de uma query de busca",
)
async def get_query(
    query_id: UUID,
    db: DbSession,
) -> SearchQueryRead:
    query_item = await QueryService.get(db, query_id)
    if not query_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query não encontrada",
        )
    return SearchQueryRead.model_validate(query_item)


@router.put(
    "/queries/{query_id}",
    response_model=SearchQueryRead,
    summary="Atualizar termo, tipo ou prioridade de uma query",
)
async def update_query(
    query_id: UUID,
    data: SearchQueryUpdate,
    db: DbSession,
) -> SearchQueryRead:
    query_item = await QueryService.get(db, query_id)
    if not query_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query não encontrada",
        )
    updated = await QueryService.update(db, query_item, data)
    return SearchQueryRead.model_validate(updated)


@router.delete(
    "/queries/{query_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir query de busca",
)
async def delete_query(
    query_id: UUID,
    db: DbSession,
) -> None:
    query_item = await QueryService.get(db, query_id)
    if not query_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query não encontrada",
        )
    await QueryService.delete(db, query_item)
