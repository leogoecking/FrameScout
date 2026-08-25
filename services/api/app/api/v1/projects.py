from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.models.entities import Project
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def _to_project_read(project: Project) -> ProjectRead:
    scenes_count = 0
    if "scenes" in project.__dict__ and project.scenes is not None:
        scenes_count = len(project.scenes)

    return ProjectRead(
        id=project.id,
        name=project.name,
        language=project.language,
        script_raw=project.script_raw,
        created_at=project.created_at,
        updated_at=project.updated_at,
        scenes_count=scenes_count,
    )


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo projeto",
)
async def create_project(
    data: ProjectCreate,
    db: DbSession,
) -> ProjectRead:
    project = await ProjectService.create(db, data)
    return _to_project_read(project)


@router.get(
    "",
    response_model=List[ProjectRead],
    summary="Listar projetos",
)
async def list_projects(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> List[ProjectRead]:
    projects = await ProjectService.list(db, skip=skip, limit=limit)
    return [_to_project_read(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Obter detalhes do projeto",
)
async def get_project(
    project_id: UUID,
    db: DbSession,
) -> ProjectRead:
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )
    return _to_project_read(project)


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Atualizar projeto ou roteiro",
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    db: DbSession,
) -> ProjectRead:
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )
    updated = await ProjectService.update(db, project, data)
    return _to_project_read(updated)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir projeto",
)
async def delete_project(
    project_id: UUID,
    db: DbSession,
) -> None:
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )
    await ProjectService.delete(db, project)
