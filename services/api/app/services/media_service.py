from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import QueryType
from app.domain.schemas import MediaCandidateBase, SearchQueryBase
from app.engine.fidelity_engine import FidelityEngine
from app.models.entities import MediaCandidate, Project, Scene, SearchQuery, SelectedAsset
from app.providers.base import MediaProvider
from app.providers.pexels import PexelsProvider
from app.providers.wikimedia import WikimediaProvider


def get_providers_map() -> Dict[str, MediaProvider]:
    return {
        "pexels": PexelsProvider(),
        "wikimedia": WikimediaProvider(),
    }


class MediaService:
    @staticmethod
    async def get(db: AsyncSession, candidate_id: UUID) -> Optional[MediaCandidate]:
        query = select(MediaCandidate).where(MediaCandidate.id == candidate_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_by_query(db: AsyncSession, search_query_id: UUID) -> List[MediaCandidate]:
        query = (
            select(MediaCandidate)
            .where(MediaCandidate.search_query_id == search_query_id)
            .order_by(
                MediaCandidate.fidelity_score.desc(),
                MediaCandidate.created_at.desc(),
            )
        )
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def list_by_scene(db: AsyncSession, scene_id: UUID) -> List[MediaCandidate]:
        query = (
            select(MediaCandidate)
            .join(SearchQuery, MediaCandidate.search_query_id == SearchQuery.id)
            .where(SearchQuery.scene_id == scene_id)
            .order_by(
                MediaCandidate.fidelity_score.desc(),
                MediaCandidate.created_at.desc(),
            )
        )
        res = await db.execute(query)
        all_candidates = list(res.scalars().all())

        # Deduplicar por external_id mantendo o melhor score
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
        provider_name: Optional[str] = None,
        limit: int = 8,
        overwrite: bool = True,
    ) -> List[MediaCandidate]:
        sq_res = await db.execute(select(SearchQuery).where(SearchQuery.id == search_query_id))
        search_query = sq_res.scalar_one_or_none()
        if not search_query:
            raise KeyError("Query de busca não encontrada")

        # Buscar dados contextuais da cena para cálculo de fidelidade
        scene_narration = ""
        scene_intent = ""
        scene_title = ""
        if search_query.scene_id:
            sc_res = await db.execute(select(Scene).where(Scene.id == search_query.scene_id))
            scene = sc_res.scalar_one_or_none()
            if scene:
                scene_narration = scene.narration
                scene_intent = scene.visual_intent or ""
                scene_title = scene.title or ""

        providers_map = get_providers_map()
        selected_providers: List[MediaProvider] = []

        q_type = (
            QueryType(search_query.query_type)
            if isinstance(search_query.query_type, str)
            else search_query.query_type
        )

        if provider_name and provider_name.lower() in providers_map:
            selected_providers.append(providers_map[provider_name.lower()])
        else:
            if q_type in [
                QueryType.EVENT,
                QueryType.OFFICIAL,
                QueryType.COMPANY,
                QueryType.PERSON,
                QueryType.LOCATION,
            ]:
                selected_providers = [
                    providers_map["wikimedia"],
                    providers_map["pexels"],
                ]
            else:
                selected_providers = [
                    providers_map["pexels"],
                    providers_map["wikimedia"],
                ]

        raw_candidates: List[MediaCandidateBase] = []
        limit_per_prov = max(1, limit // len(selected_providers))

        for prov in selected_providers:
            results = await prov.search(
                query=SearchQueryBase(
                    query=search_query.query,
                    query_type=q_type,
                    priority=search_query.priority,
                ),
                limit=limit_per_prov,
            )
            raw_candidates.extend(results)

        if overwrite:
            del_stmt = delete(MediaCandidate).where(
                MediaCandidate.search_query_id == search_query_id
            )
            await db.execute(del_stmt)

        created_entities: List[MediaCandidate] = []
        seen_ext: Set[str] = set()

        for rc in raw_candidates:
            if rc.external_id in seen_ext:
                continue
            seen_ext.add(rc.external_id)

            # Calcular Fidelity Score (0 a 100)
            score, breakdown = FidelityEngine.calculate_score(
                scene_narration=scene_narration,
                scene_visual_intent=scene_intent,
                scene_title=scene_title,
                media_title=rc.title,
                media_provider=rc.provider,
                media_width=rc.width,
                media_height=rc.height,
                media_type=rc.media_type.value
                if hasattr(rc.media_type, "value")
                else str(rc.media_type),
                metadata_json=rc.metadata_json,
            )

            meta: Dict[str, Any] = dict(rc.metadata_json or {})
            meta["fidelity_breakdown"] = breakdown

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
                fidelity_score=score / 100.0,
                metadata_json=meta,
            )
            db.add(mc)
            created_entities.append(mc)

        await db.commit()
        for c in created_entities:
            await db.refresh(c)

        # Ordenar por score decrescente
        created_entities.sort(key=lambda x: x.fidelity_score or 0.0, reverse=True)
        return created_entities

    @staticmethod
    async def search_for_scene(
        db: AsyncSession,
        scene_id: UUID,
        provider_name: Optional[str] = None,
        limit_per_query: int = 4,
    ) -> List[MediaCandidate]:
        scene_res = await db.execute(select(Scene).where(Scene.id == scene_id))
        scene = scene_res.scalar_one_or_none()
        if not scene:
            raise KeyError("Cena não encontrada")

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
                provider_name=provider_name,
                limit=limit_per_query,
                overwrite=True,
            )
            all_candidates.extend(candidates)

        seen_external: Set[str] = set()
        deduped: List[MediaCandidate] = []
        for c in all_candidates:
            if c.external_id not in seen_external:
                seen_external.add(c.external_id)
                deduped.append(c)

        deduped.sort(key=lambda x: x.fidelity_score or 0.0, reverse=True)
        return deduped

    @staticmethod
    async def rerank_scene_candidates(db: AsyncSession, scene_id: UUID) -> List[MediaCandidate]:
        """
        Recalcula o Fidelity Score para todos os candidatos vinculados a uma cena.
        """
        sc_res = await db.execute(
            select(Scene)
            .options(
                selectinload(Scene.selected_assets).selectinload(SelectedAsset.media_candidate)
            )
            .where(Scene.id == scene_id)
        )
        scene = sc_res.scalar_one_or_none()
        if not scene:
            raise KeyError("Cena não encontrada")

        candidates = await MediaService.list_by_scene(db, scene_id)
        candidate_ids = {c.id for c in candidates}

        # Incluir também candidatos que estão nos selected_assets da cena
        for sa in scene.selected_assets:
            if sa.media_candidate and sa.media_candidate.id not in candidate_ids:
                candidates.append(sa.media_candidate)
                candidate_ids.add(sa.media_candidate.id)

        for c in candidates:
            score, breakdown = FidelityEngine.calculate_score(
                scene_narration=scene.narration,
                scene_visual_intent=scene.visual_intent,
                scene_title=scene.title,
                media_title=c.title,
                media_provider=c.provider,
                media_width=c.width,
                media_height=c.height,
                media_type=c.media_type.value
                if hasattr(c.media_type, "value")
                else str(c.media_type),
                metadata_json=c.metadata_json,
            )
            meta: Dict[str, Any] = dict(c.metadata_json or {})
            meta["fidelity_breakdown"] = breakdown
            c.metadata_json = meta
            c.fidelity_score = score / 100.0

        await db.commit()
        for c in candidates:
            await db.refresh(c)

        candidates.sort(key=lambda x: x.fidelity_score or 0.0, reverse=True)
        return candidates

    @staticmethod
    async def get_project_fidelity_metrics(db: AsyncSession, project_id: UUID) -> Dict[str, Any]:
        """
        Calcula as métricas consolidadas de fidelidade do projeto.
        """
        proj_res = await db.execute(
            select(Project)
            .options(
                selectinload(Project.scenes)
                .selectinload(Scene.selected_assets)
                .selectinload(SelectedAsset.media_candidate),
                selectinload(Project.scenes)
                .selectinload(Scene.queries)
                .selectinload(SearchQuery.media_candidates),
            )
            .where(Project.id == project_id)
        )
        project = proj_res.scalar_one_or_none()
        if not project:
            raise KeyError("Projeto não encontrado")

        total_scenes = len(project.scenes)
        if total_scenes == 0:
            return {
                "average_fidelity": 0,
                "high_fidelity_count": 0,
                "broll_count": 0,
                "reference_count": 0,
                "scenes_covered": 0,
                "total_scenes": 0,
            }

        scores: List[float] = []
        high_fid = 0
        broll = 0
        ref_count = 0
        covered_scenes = 0

        for s in project.scenes:
            target_candidate: Optional[MediaCandidate] = None
            if s.selected_assets and s.selected_assets[0].media_candidate:
                target_candidate = s.selected_assets[0].media_candidate
            else:
                for q in s.queries:
                    if q.media_candidates:
                        target_candidate = q.media_candidates[0]
                        break

            if target_candidate and target_candidate.fidelity_score is not None:
                covered_scenes += 1
                fid_val = round(target_candidate.fidelity_score * 100.0)
                scores.append(fid_val)
                if fid_val >= 80:
                    high_fid += 1
                elif fid_val >= 50:
                    broll += 1
                else:
                    ref_count += 1

        avg_score = round(sum(scores) / len(scores)) if scores else 0

        return {
            "average_fidelity": avg_score,
            "high_fidelity_count": high_fid,
            "broll_count": broll,
            "reference_count": ref_count,
            "scenes_covered": covered_scenes,
            "total_scenes": total_scenes,
        }
