from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.schemas import (
    SelectedAssetCreate,
    SelectedAssetRead,
    SelectedAssetUpdate,
    VisualPlanExport,
)
from app.services.asset_service import AssetService
from app.services.visual_plan_service import VisualPlanService

router = APIRouter(tags=["Selected Assets & Visual Plan"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.post(
    "/scenes/{scene_id}/assets/select",
    response_model=SelectedAssetRead,
    status_code=status.HTTP_201_CREATED,
    summary="Selecionar e fixar um candidato de mídia na cena",
)
async def select_asset_for_scene(
    scene_id: UUID,
    data: SelectedAssetCreate,
    db: DbSession,
) -> SelectedAssetRead:
    try:
        asset = await AssetService.select_asset(db, scene_id, data)
        return SelectedAssetRead.model_validate(asset)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e


@router.get(
    "/scenes/{scene_id}/assets",
    response_model=List[SelectedAssetRead],
    summary="Listar assets selecionados para a cena",
)
async def list_scene_selected_assets(
    scene_id: UUID,
    db: DbSession,
) -> List[SelectedAssetRead]:
    assets = await AssetService.list_by_scene(db, scene_id)
    return [SelectedAssetRead.model_validate(a) for a in assets]


@router.put(
    "/selected-assets/{asset_id}",
    response_model=SelectedAssetRead,
    summary="Atualizar configurações de um asset selecionado (enquadramento, notas)",
)
async def update_selected_asset(
    asset_id: UUID,
    data: SelectedAssetUpdate,
    db: DbSession,
) -> SelectedAssetRead:
    try:
        updated = await AssetService.update_selected_asset(db, asset_id, data)
        return SelectedAssetRead.model_validate(updated)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e


@router.delete(
    "/selected-assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover seleção de mídia da cena",
)
async def remove_selected_asset(
    asset_id: UUID,
    db: DbSession,
) -> None:
    try:
        await AssetService.remove_selected_asset(db, asset_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e


@router.get(
    "/projects/{project_id}/visual-plan",
    response_model=VisualPlanExport,
    summary="Gerar e exportar o Plano de Produção Visual com créditos consolidados",
)
async def export_project_visual_plan(
    project_id: UUID,
    db: DbSession,
) -> VisualPlanExport:
    try:
        return await VisualPlanService.generate_visual_plan(db, project_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e
