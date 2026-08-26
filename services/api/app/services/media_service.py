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
from app.providers.gemini_imagen import GeminiImagenProvider
from app.providers.nasa import NASAProvider
from app.providers.openverse import OpenverseProvider
from app.providers.pexels import PexelsProvider
from app.providers.wikimedia import WikimediaProvider


def get_providers_map() -> Dict[str, MediaProvider]:
    return {
        "wikimedia": WikimediaProvider(),
        "openverse": OpenverseProvider(),
        "nasa": NASAProvider(),
        "pexels": PexelsProvider(),
        "gemini": GeminiImagenProvider(),
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

        query_str_lower = search_query.query.lower()
        is_space_or_science = any(
            w in query_str_lower
            for w in [
                "space",
                "espaço",
                "espaco",
                "nasa",
                "astronaut",
                "astronauta",
                "planet",
                "planeta",
                "moon",
                "lua",
                "mars",
                "marte",
                "galaxy",
                "galáxia",
                "telescop",
                "rocket",
                "foguete",
                "science",
                "ciência",
            ]
        )

        if provider_name and provider_name.lower() in providers_map:
            selected_providers.append(providers_map[provider_name.lower()])
        else:
            if is_space_or_science:
                selected_providers = [
                    providers_map["nasa"],
                    providers_map["wikimedia"],
                    providers_map["openverse"],
                    providers_map["pexels"],
                ]
            elif q_type in [
                QueryType.EVENT,
                QueryType.OFFICIAL,
                QueryType.COMPANY,
                QueryType.PERSON,
                QueryType.LOCATION,
            ]:
                selected_providers = [
                    providers_map["wikimedia"],
                    providers_map["openverse"],
                    providers_map["pexels"],
                ]
            else:
                selected_providers = [
                    providers_map["openverse"],
                    providers_map["pexels"],
                    providers_map["wikimedia"],
                ]

        raw_candidates: List[MediaCandidateBase] = []
        limit_per_prov = max(2, (limit + len(selected_providers) - 1) // len(selected_providers))

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

        scored_candidates: List[tuple[float, Dict[str, Any], MediaCandidateBase]] = []
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
                media_title=rc.title or "",
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
            scored_candidates.append((score / 100.0, meta, rc))

        # Ordenar por score decrescente e persistir apenas os melhores até o limit
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_candidates[:limit]

        created_entities: List[MediaCandidate] = []
        for s_val, s_meta, rc in top_candidates:
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
                fidelity_score=s_val,
                metadata_json=s_meta,
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

    @staticmethod
    async def generate_ai_for_scene(
        db: AsyncSession,
        scene_id: UUID,
        prompt_override: Optional[str] = None,
        aspect_ratio: str = "16:9",
        count: int = 2,
    ) -> List[MediaCandidate]:
        scene_query = (
            select(Scene).options(selectinload(Scene.queries)).where(Scene.id == scene_id)
        )
        scene_res = await db.execute(scene_query)
        scene = scene_res.scalar_one_or_none()
        if not scene:
            raise KeyError("Cena não encontrada")

        # Determinar o prompt visual ideal
        if prompt_override and prompt_override.strip():
            final_prompt = prompt_override.strip()
        elif scene.visual_intent and len(scene.visual_intent.strip()) > 5:
            final_prompt = f"{scene.visual_intent}. {scene.narration[:120]}"
        else:
            final_prompt = f"{scene.title or ''}. {scene.narration}"

        gemini_provider = GeminiImagenProvider()
        ai_candidates = await gemini_provider.generate_image(
            prompt=final_prompt,
            aspect_ratio=aspect_ratio,
            sample_count=count,
        )

        target_query_id: Optional[UUID] = None
        if scene.queries:
            target_query_id = scene.queries[0].id
        else:
            ai_query = SearchQuery(
                scene_id=scene.id,
                query=final_prompt[:80],
                query_type=QueryType.CONCEPT,
                priority=1,
            )
            db.add(ai_query)
            await db.flush()
            target_query_id = ai_query.id

        persisted_candidates: List[MediaCandidate] = []
        for c in ai_candidates:
            cand_obj = MediaCandidate(
                search_query_id=target_query_id,
                provider=c.provider,
                external_id=c.external_id,
                title=c.title,
                url=c.url,
                preview_url=c.preview_url,
                media_type=c.media_type,
                width=c.width,
                height=c.height,
                duration=c.duration,
                author=c.author,
                license=c.license,
                attribution=c.attribution,
                rights_status=c.rights_status,
                fidelity_score=0.96,
                metadata_json=c.metadata_json,
            )
            db.add(cand_obj)
            persisted_candidates.append(cand_obj)

        await db.commit()
        for cand_obj in persisted_candidates:
            await db.refresh(cand_obj)

        return persisted_candidates

