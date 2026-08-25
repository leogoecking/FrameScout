import asyncio
from typing import Annotated, Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, get_db_session
from app.domain.schemas import RenderJobCreate, RenderJobRead
from app.engine.tts_engine import TTSEngine
from app.services.render_service import RenderService

router = APIRouter(tags=["Video Rendering Engine"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get(
    "/voices",
    response_model=List[Dict[str, str]],
    summary="Listar vozes neurais disponíveis para síntese de voz (TTS)",
)
async def list_available_voices() -> List[Dict[str, str]]:
    return TTSEngine.list_voices()


@router.post(
    "/projects/{project_id}/render",
    response_model=RenderJobRead,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar job de renderização de vídeo completo para o projeto",
)
async def trigger_render_job(
    project_id: UUID,
    data: RenderJobCreate,
    db: DbSession,
) -> RenderJobRead:
    try:
        job = await RenderService.create_job(db, project_id, data)

        # Disparar pipeline em background assíncrono
        asyncio.create_task(
            RenderService.execute_render_pipeline(
                job_id=job.id,
                project_id=project_id,
                session_factory=AsyncSessionLocal,
            )
        )

        return RenderJobRead.model_validate(job)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e).strip("'\""),
        ) from e


@router.get(
    "/projects/{project_id}/render-jobs",
    response_model=List[RenderJobRead],
    summary="Listar histórico de jobs de renderização do projeto",
)
async def list_project_render_jobs(
    project_id: UUID,
    db: DbSession,
) -> List[RenderJobRead]:
    jobs = await RenderService.list_by_project(db, project_id)
    return [RenderJobRead.model_validate(j) for j in jobs]


@router.get(
    "/render-jobs/{job_id}",
    response_model=RenderJobRead,
    summary="Consultar status e progresso de um job de renderização",
)
async def get_render_job(
    job_id: UUID,
    db: DbSession,
) -> RenderJobRead:
    job = await RenderService.get(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job de renderização não encontrado",
        )
    return RenderJobRead.model_validate(job)


@router.get(
    "/render-jobs/{job_id}/stream",
    summary="Download ou streaming do vídeo MP4 finalizado",
)
async def stream_rendered_video(
    job_id: UUID,
    db: DbSession,
) -> Any:
    job = await RenderService.get(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job de renderização não encontrado",
        )

    video_path = RenderService.get_rendered_video_path(job_id)
    if not video_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo de vídeo ainda não disponível ou em processamento.",
        )

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"framescout-video-{job_id}.mp4",
    )
