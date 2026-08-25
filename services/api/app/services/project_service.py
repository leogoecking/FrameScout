from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.schemas import ProjectCreate, ProjectUpdate
from app.models.entities import Project


class ProjectService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ProjectCreate) -> Project:
        project = Project(
            name=obj_in.name,
            language=obj_in.language,
            script_raw=obj_in.script_raw,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def list(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Project]:
        query = (
            select(Project)
            .options(selectinload(Project.scenes))
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get(db: AsyncSession, project_id: UUID) -> Optional[Project]:
        query = (
            select(Project).options(selectinload(Project.scenes)).where(Project.id == project_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, project: Project, obj_in: ProjectUpdate) -> Project:
        if obj_in.name is not None:
            project.name = obj_in.name
        if obj_in.language is not None:
            project.language = obj_in.language
        if obj_in.script_raw is not None:
            project.script_raw = obj_in.script_raw

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete(db: AsyncSession, project: Project) -> None:
        await db.delete(project)
        await db.commit()
