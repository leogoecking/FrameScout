from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.schemas import SelectedAssetCreate, SelectedAssetUpdate
from app.models.entities import MediaCandidate, Scene, SelectedAsset


class AssetService:
    @staticmethod
    async def get(db: AsyncSession, selected_asset_id: UUID) -> Optional[SelectedAsset]:
        query = (
            select(SelectedAsset)
            .options(selectinload(SelectedAsset.media_candidate))
            .where(SelectedAsset.id == selected_asset_id)
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_by_scene(db: AsyncSession, scene_id: UUID) -> List[SelectedAsset]:
        query = (
            select(SelectedAsset)
            .options(selectinload(SelectedAsset.media_candidate))
            .where(SelectedAsset.scene_id == scene_id)
            .order_by(SelectedAsset.order_index.asc(), SelectedAsset.created_at.asc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def select_asset(
        db: AsyncSession, scene_id: UUID, data: SelectedAssetCreate
    ) -> SelectedAsset:
        # 1. Validar que a cena existe
        scene_res = await db.execute(select(Scene).where(Scene.id == scene_id))
        scene = scene_res.scalar_one_or_none()
        if not scene:
            raise KeyError("Cena não encontrada")

        # 2. Validar que o candidato de mídia existe
        cand_res = await db.execute(
            select(MediaCandidate).where(MediaCandidate.id == data.media_candidate_id)
        )
        candidate = cand_res.scalar_one_or_none()
        if not candidate:
            raise KeyError("Candidato de mídia não encontrado")

        # 3. Remover seleção anterior para a mesma cena se já existir (para curadoria direta 1:1)
        await db.execute(delete(SelectedAsset).where(SelectedAsset.scene_id == scene_id))

        # 4. Criar o asset selecionado
        selected = SelectedAsset(
            scene_id=scene_id,
            media_candidate_id=data.media_candidate_id,
            order_index=data.order_index or 0,
            framing_mode=data.framing_mode or "FILL",
            notes=data.notes,
        )
        db.add(selected)
        await db.commit()

        # Recarregar com eager-loading do candidato de mídia
        return await AssetService.get(db, selected.id)  # type: ignore[return-value]

    @staticmethod
    async def update_selected_asset(
        db: AsyncSession, selected_asset_id: UUID, data: SelectedAssetUpdate
    ) -> SelectedAsset:
        selected = await AssetService.get(db, selected_asset_id)
        if not selected:
            raise KeyError("Asset selecionado não encontrado")

        if data.framing_mode is not None:
            selected.framing_mode = data.framing_mode
        if data.order_index is not None:
            selected.order_index = data.order_index
        if data.notes is not None:
            selected.notes = data.notes

        await db.commit()
        return await AssetService.get(db, selected_asset_id)  # type: ignore[return-value]

    @staticmethod
    async def remove_selected_asset(db: AsyncSession, selected_asset_id: UUID) -> None:
        selected = await AssetService.get(db, selected_asset_id)
        if not selected:
            raise KeyError("Asset selecionado não encontrado")

        await db.delete(selected)
        await db.commit()
