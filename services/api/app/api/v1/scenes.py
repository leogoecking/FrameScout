from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.schemas import (
    SceneCreate,
    SceneMergeRequest,
    SceneRead,
    SceneReorderRequest,
    SceneSplitRequest,
    SceneUpdate,
)
from app.services.scene_service import SceneService

router = APIRouter(tags=["Scenes"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


# --- Project-Scoped Scene Endpoints ---

@router.post(
    "/projects/{project_id}/scenes/generate",
    response_model=List[SceneRead],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar cenas automaticamente a partir do roteiro",
)
async def generate_scenes(
    project_id: UUID,
    db: DbSession,
) -> List[SceneRead]:
    try:
        scenes = await SceneService.generate_from_script(db, project_id)
        return [SceneRead.model_validate(s) for s in scenes]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "/projects/{project_id}/scenes",
    response_model=List[SceneRead],
    summary="Listar cenas do projeto",
)
async def list_project_scenes(
    project_id: UUID,
    db: DbSession,
) -> List[SceneRead]:
    scenes = await SceneService.list_by_project(db, project_id)
    return [SceneRead.model_validate(s) for s in scenes]


@router.post(
    "/projects/{project_id}/scenes",
    response_model=SceneRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar cena manualmente",
)
async def create_scene(
    project_id: UUID,
    data: SceneCreate,
    db: DbSession,
) -> SceneRead:
    scene = await SceneService.create(db, project_id, data)
    return SceneRead.model_validate(scene)


@router.put(
    "/projects/{project_id}/scenes/reorder",
    response_model=List[SceneRead],
    summary="Reordenar sequência de cenas",
)
async def reorder_scenes(
    project_id: UUID,
    req: SceneReorderRequest,
    db: DbSession,
) -> List[SceneRead]:
    scenes = await SceneService.reorder(db, project_id, req.scene_ids)
    return [SceneRead.model_validate(s) for s in scenes]


# --- Individual Scene Endpoints ---

@router.get(
    "/scenes/{scene_id}",
    response_model=SceneRead,
    summary="Obter detalhes de uma cena",
)
async def get_scene(
    scene_id: UUID,
    db: DbSession,
) -> SceneRead:
    scene = await SceneService.get(db, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada",
        )
    return SceneRead.model_validate(scene)


@router.put(
    "/scenes/{scene_id}",
    response_model=SceneRead,
    summary="Atualizar cena",
)
async def update_scene(
    scene_id: UUID,
    data: SceneUpdate,
    db: DbSession,
) -> SceneRead:
    scene = await SceneService.get(db, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada",
        )
    updated = await SceneService.update(db, scene, data)
    return SceneRead.model_validate(updated)


@router.delete(
    "/scenes/{scene_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir cena",
)
async def delete_scene(
    scene_id: UUID,
    db: DbSession,
) -> None:
    scene = await SceneService.get(db, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada",
        )
    await SceneService.delete(db, scene)


@router.post(
    "/scenes/{scene_id}/split",
    response_model=List[SceneRead],
    summary="Dividir uma cena em duas",
)
async def split_scene(
    scene_id: UUID,
    req: SceneSplitRequest,
    db: DbSession,
) -> List[SceneRead]:
    scene = await SceneService.get(db, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada",
        )
    scenes = await SceneService.split(db, scene, req)
    return [SceneRead.model_validate(s) for s in scenes]


@router.post(
    "/scenes/{scene_id}/merge",
    response_model=SceneRead,
    summary="Unir cena com outra adjacente",
)
async def merge_scenes(
    scene_id: UUID,
    req: SceneMergeRequest,
    db: DbSession,
) -> SceneRead:
    scene = await SceneService.get(db, scene_id)
    if not scene:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cena não encontrada",
        )
    try:
        merged = await SceneService.merge(db, scene, req)
        return SceneRead.model_validate(merged)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
