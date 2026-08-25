from typing import List, Optional, Set
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import SearchQueryBase
from app.models.entities import MediaCandidate, Scene, SearchQuery
from app.providers.pexels import PexelsProvider


class MediaService:
    @staticmethod
    async def get(db: AsyncSession, candidate_id: UUID) -> Optional[MediaCandidate]:
        query = select(MediaCandidate).where(MediaCandidate.id == candidate_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_by_query(
        db: AsyncSession, search_query_id: UUID
    ) -> List[MediaCandidate]:
        query = (
            select(MediaCandidate)
            .where(MediaCandidate.search_query_id == search_query_id)
            .order_by(MediaCandidate.fidelity_score.desc(), MediaCandidate.created_at.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def list_by_scene(
        db: AsyncSession, scene_id: UUID
    ) -> List[MediaCandidate]:
        # Busca todos os candidatos vinculados a quaisquer queries da cena
        query = (
            select(MediaCandidate)
            .join(SearchQuery, MediaCandidate.search_query_id == SearchQuery.id)
            .where(SearchQuery.scene_id == scene_id)
            .order_by(MediaCandidate.fidelity_score.desc(), MediaCandidate.created_at.desc())
        )
        res = await db.execute(query)
        all_candidates = list(res.scalars().all())

        # Deduplicar por external_id mantendo o melhor ranqueamento
        seen_external: Set[str] = set()
        deduped_candidates: List[MediaCandidate] = []
        for candidate in all_candidates:
            if candidate.external_id not in seen_external:
                seen_external.add(candidate.external_id)
                deduped_candidates.append(candidate)

        return deduped_candidates

    @staticmethod
    async def search_for_query(
        db: AsyncSession,
        search_query_id: UUID,
        limit: int = 8,
        overwrite: bool = True,
    ) -> List[MediaCandidate]:
        sq_res = await db.execute(
            select(SearchQuery).where(SearchQuery.id == search_query_id)
        )
        search_query = sq_res.scalar_one_or_none()
        if not search_query:
            raise KeyError("Query de busca não encontrada")

        provider = PexelsProvider()
        raw_candidates = await provider.search(
            query=SearchQueryBase(
                query=search_query.query,
                query_type=search_query.query_type,
                priority=search_query.priority,
            ),
            limit=limit,
        )

        if overwrite:
            del_stmt = delete(MediaCandidate).where(
                MediaCandidate.search_query_id == search_query_id
            )
            await db.execute(del_stmt)

        created_entities: List[MediaCandidate] = []
        for rc in raw_candidates:
            mc = MediaCandidate(
                search_query_id=search_query_id,
                provider=rc.provider,
                external_id=rc.external_id,
                title=rc.title,
                url=rc.url,
                preview_url=rc.preview_url,
                media_type=rc.media_type,
                width=rc.width,
                height=rc.height,
                duration=rc.duration,
                author=rc.author,
                license=rc.license,
                attribution=rc.attribution,
                rights_status=rc.rights_status,
                fidelity_score=rc.fidelity_score,
                metadata_json=rc.metadata_json,
            )
            db.add(mc)
            created_entities.append(mc)

        await db.commit()
        for c in created_entities:
            await db.refresh(c)

        return created_entities

    @staticmethod
    async def search_for_scene(
        db: AsyncSession,
        scene_id: UUID,
        limit_per_query: int = 4,
    ) -> List[MediaCandidate]:
        scene_res = await db.execute(select(Scene).where(Scene.id == scene_id))
        scene = scene_res.scalar_one_or_none()
        if not scene:
            raise KeyError("Cena não encontrada")

        # Buscar todas as queries da cena
        queries_res = await db.execute(
            select(SearchQuery)
            .where(SearchQuery.scene_id == scene_id)
            .order_by(SearchQuery.priority.asc())
        )
        queries = list(queries_res.scalars().all())

        if not queries:
            raise ValueError("A cena não possui queries geradas para realizar a busca de mídia.")

        all_candidates: List[MediaCandidate] = []
        for q in queries:
            candidates = await MediaService.search_for_query(
                db=db,
                search_query_id=q.id,
                limit=limit_per_query,
                overwrite=True,
            )
            all_candidates.extend(candidates)

        # Deduplicar por external_id
        seen_external: Set[str] = set()
        deduped: List[MediaCandidate] = []
        for c in all_candidates:
            if c.external_id not in seen_external:
                seen_external.add(c.external_id)
                deduped.append(c)

        return deduped
