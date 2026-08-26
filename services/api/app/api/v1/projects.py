from typing import Annotated, Dict, List, Set
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.enums import ScriptTone
from app.domain.schemas import (
    GenerateScriptRequest,
    GenerateScriptResponse,
    ProjectCreate,
    ProjectEntitiesResponse,
    ProjectRead,
    ProjectUpdate,
    SceneEntitiesResponse,
)
from app.engine.entity_engine import EntityEngine
from app.engine.script_engine import ScriptEngine
from app.models.entities import Project
from app.services.project_service import ProjectService
from app.services.scene_service import SceneService

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


@router.post(
    "/{project_id}/entities/extract",
    response_model=ProjectEntitiesResponse,
    summary="Extrair panorama consolidado de entidades de todo o projeto",
)
async def extract_project_entities(
    project_id: UUID,
    db: DbSession,
) -> ProjectEntitiesResponse:
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    scenes_entities: List[SceneEntitiesResponse] = []
    entities_by_cat: Dict[str, Set[str]] = {
        "ORGANIZATION": set(),
        "PRODUCT": set(),
        "PERSON": set(),
        "TECHNOLOGY": set(),
        "LOCATION": set(),
        "DATE_TIME": set(),
        "EVENT": set(),
    }
    total_count = 0

    scenes = sorted(project.scenes or [], key=lambda s: s.position)
    for sc in scenes:
        c_text = f"{sc.title or ''} {sc.narration} {sc.visual_intent or ''}".strip()
        sc_ents = EntityEngine.extract_entities(c_text)
        sc_queries = EntityEngine.generate_queries_from_entities(sc_ents, sc.title or "")

        for ent in sc_ents:
            cat_name = ent.category.value if hasattr(ent.category, "value") else str(ent.category)
            if cat_name in entities_by_cat:
                entities_by_cat[cat_name].add(ent.text)
            total_count += 1

        scenes_entities.append(
            SceneEntitiesResponse(
                scene_id=sc.id,
                scene_position=sc.position,
                entities=sc_ents,
                suggested_queries=sc_queries,
            )
        )

    return ProjectEntitiesResponse(
        project_id=project.id,
        total_entities_count=total_count,
        entities_by_category={k: sorted(list(v)) for k, v in entities_by_cat.items()},
        scenes_entities=scenes_entities,
    )


@router.post(
    "/generate-script",
    response_model=GenerateScriptResponse,
    summary="Gerar roteiro de vídeo estruturado por IA a partir de um tema com Gemini",
)
async def generate_script(
    data: GenerateScriptRequest,
) -> GenerateScriptResponse:
    return await ScriptEngine.generate_script(
        topic=data.topic,
        tone=data.tone or ScriptTone.DOCUMENTARY,
        target_duration=data.target_duration or "3m",
        language=data.target_language or "pt-BR",
        context_notes=data.context_notes,
    )


@router.post(
    "/{project_id}/generate-script",
    response_model=GenerateScriptResponse,
    summary="Gerar roteiro com IA e aplicar diretamente no projeto",
)
async def generate_project_script(
    project_id: UUID,
    data: GenerateScriptRequest,
    db: DbSession,
) -> GenerateScriptResponse:
    project = await ProjectService.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    gen_res = await ScriptEngine.generate_script(
        topic=data.topic,
        tone=data.tone or ScriptTone.DOCUMENTARY,
        target_duration=data.target_duration or "3m",
        language=data.target_language or project.language or "pt-BR",
        context_notes=data.context_notes,
    )

    # Atualizar script_raw do projeto
    project.script_raw = gen_res.script_raw
    await db.commit()
    await db.refresh(project)

    # Se auto_generate_scenes for True, gera cenas automaticamente a partir do novo roteiro
    if data.auto_generate_scenes:
        await SceneService.generate_from_script(db, project_id)

    return gen_res

