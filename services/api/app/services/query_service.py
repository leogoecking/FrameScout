from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas import SearchQueryCreate, SearchQueryUpdate
from app.models.entities import Project, Scene, SearchQuery
from app.services.query_generator import QueryGenerator


class QueryService:
    @staticmethod
    async def list_by_scene(db: AsyncSession, scene_id: UUID) -> List[SearchQuery]:
        query = (
            select(SearchQuery)
            .where(SearchQuery.scene_id == scene_id)
            .order_by(SearchQuery.priority.asc(), SearchQuery.created_at.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get(db: AsyncSession, query_id: UUID) -> Optional[SearchQuery]:
        query = select(SearchQuery).where(SearchQuery.id == query_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def generate_for_scene(
        db: AsyncSession, scene_id: UUID, overwrite: bool = True
    ) -> List[SearchQuery]:
        scene_query = select(Scene).where(Scene.id == scene_id)
        scene_res = await db.execute(scene_query)
        scene = scene_res.scalar_one_or_none()

        if not scene:
            raise ValueError("Cena não encontrada")

        generated_queries = QueryGenerator.generate(
            narration=scene.narration,
            visual_intent=scene.visual_intent,
            title=scene.title,
        )

        if overwrite:
            del_stmt = delete(SearchQuery).where(SearchQuery.scene_id == scene_id)
            await db.execute(del_stmt)

        created_queries: List[SearchQuery] = []
        for q in generated_queries:
            sq = SearchQuery(
                scene_id=scene_id,
                query=q.query,
                query_type=q.query_type,
                priority=q.priority,
            )
            db.add(sq)
            created_queries.append(sq)

        await db.commit()
        for sq in created_queries:
            await db.refresh(sq)

        return created_queries

    @staticmethod
    async def generate_for_project(
        db: AsyncSession, project_id: UUID, overwrite: bool = True
    ) -> Dict[str, int]:
        proj_query = select(Project).where(Project.id == project_id)
        proj_res = await db.execute(proj_query)
        project = proj_res.scalar_one_or_none()

        if not project:
            raise ValueError("Projeto não encontrado")

        scenes_query = (
            select(Scene)
            .where(Scene.project_id == project_id)
            .order_by(Scene.position.asc())
        )
        scenes_res = await db.execute(scenes_query)
        scenes = list(scenes_res.scalars().all())

        if not scenes:
            raise ValueError("O projeto não possui cenas geradas para criar queries.")

        total_queries = 0
        for scene in scenes:
            queries = await QueryService.generate_for_scene(
                db, scene.id, overwrite=overwrite
            )
            total_queries += len(queries)

        return {"scenes_count": len(scenes), "total_queries_created": total_queries}

    @staticmethod
    async def create(
        db: AsyncSession, scene_id: UUID, obj_in: SearchQueryCreate
    ) -> SearchQuery:
        scene_query = select(Scene).where(Scene.id == scene_id)
        scene_res = await db.execute(scene_query)
        scene = scene_res.scalar_one_or_none()

        if not scene:
            raise ValueError("Cena não encontrada")

        sq = SearchQuery(
            scene_id=scene_id,
            query=obj_in.query.strip(),
            query_type=obj_in.query_type,
            priority=obj_in.priority,
        )
        db.add(sq)
        await db.commit()
        await db.refresh(sq)
        return sq

    @staticmethod
    async def update(
        db: AsyncSession, query_item: SearchQuery, obj_in: SearchQueryUpdate
    ) -> SearchQuery:
        if obj_in.query is not None:
            query_item.query = obj_in.query.strip()
        if obj_in.query_type is not None:
            query_item.query_type = obj_in.query_type
        if obj_in.priority is not None:
            query_item.priority = obj_in.priority

        await db.commit()
        await db.refresh(query_item)
        return query_item

    @staticmethod
    async def delete(db: AsyncSession, query_item: SearchQuery) -> None:
        await db.delete(query_item)
        await db.commit()
