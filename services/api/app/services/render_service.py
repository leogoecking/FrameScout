import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import RenderStatus
from app.domain.schemas import RenderJobCreate
from app.engine.tts_engine import TTSEngine
from app.engine.video_composer import VideoComposer
from app.models.entities import (
    MediaCandidate,
    Project,
    RenderJob,
    Scene,
    SearchQuery,
    SelectedAsset,
)

logger = logging.getLogger("framescout.services.render")

STORAGE_BASE_DIR = os.getenv("STORAGE_LOCAL_DIR", "./media_storage")
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36 FrameScoutBot/1.0"
    )
}


class RenderService:
    @staticmethod
    def get_video_storage_dir() -> Path:
        p = Path(STORAGE_BASE_DIR) / "rendered_videos"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def get_rendered_video_path(job_id: UUID) -> Path:
        return RenderService.get_video_storage_dir() / f"{job_id}.mp4"

    @staticmethod
    async def get(db: AsyncSession, job_id: UUID) -> Optional[RenderJob]:
        query = select(RenderJob).where(RenderJob.id == job_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_by_project(db: AsyncSession, project_id: UUID) -> List[RenderJob]:
        query = (
            select(RenderJob)
            .where(RenderJob.project_id == project_id)
            .order_by(RenderJob.created_at.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def create_job(db: AsyncSession, project_id: UUID, data: RenderJobCreate) -> RenderJob:
        proj_res = await db.execute(select(Project).where(Project.id == project_id))
        project = proj_res.scalar_one_or_none()
        if not project:
            raise KeyError("Projeto não encontrado")

        include_subs = data.include_subtitles if data.include_subtitles is not None else True
        include_cred = data.include_credits_card if data.include_credits_card is not None else True

        job = RenderJob(
            project_id=project_id,
            status=RenderStatus.PENDING,
            progress=0,
            aspect_ratio=data.aspect_ratio or "16:9",
            voice=data.voice or "pt-BR-AntonioNeural",
            include_subtitles=include_subs,
            include_credits_card=include_cred,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @staticmethod
    def _sanitize_media_url(url: str) -> str:
        """Ajusta URLs de thumbnails de provedores que exigem dimensões específicas."""
        if not url:
            return ""
        # Wikimedia commons: converter 800px para 960px caso presente em thumbnails
        if "upload.wikimedia.org" in url and "/800px-" in url:
            return url.replace("/800px-", "/960px-")
        return url

    @staticmethod
    async def execute_render_pipeline(
        job_id: UUID,
        project_id: UUID,
        session_factory,
    ) -> None:
        """
        Pipeline assíncrono completo de montagem e renderização do vídeo.
        """
        temp_dir = tempfile.mkdtemp(prefix=f"framescout_render_{job_id}_")
        try:
            async with session_factory() as db:
                job = await RenderService.get(db, job_id)
                if not job:
                    return

                # 1. Carregar projeto com cenas, queries, assets selecionados e candidatos
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
                if not project or not project.scenes:
                    job.status = RenderStatus.FAILED
                    job.error_message = "O projeto não possui cenas para renderizar."
                    await db.commit()
                    return

                # 2. Etapa 1: Síntese de Voz (TTS)
                job.status = RenderStatus.SYNTHESIZING_AUDIO
                job.progress = 15
                await db.commit()

                scene_audios: List[Tuple[str, float]] = []
                total_duration = 0.0

                for idx, scene in enumerate(project.scenes):
                    audio_path = os.path.join(temp_dir, f"scene_{idx:03d}_audio.mp3")
                    duration = await TTSEngine.synthesize(
                        text=scene.narration,
                        voice=job.voice,
                        output_path=audio_path,
                    )
                    scene_audios.append((audio_path, duration))
                    total_duration += duration

                # 3. Etapa 2: Download de Mídias e Composição Visual
                job.status = RenderStatus.PROCESSING_MEDIA
                job.progress = 45
                await db.commit()

                scene_clips: List[str] = []
                attributions_set = set()

                async with httpx.AsyncClient(
                    timeout=30.0, follow_redirects=True, headers=HTTP_HEADERS
                ) as http_client:
                    for idx, scene in enumerate(project.scenes):
                        audio_path, duration = scene_audios[idx]
                        clip_path = os.path.join(temp_dir, f"scene_{idx:03d}_clip.mp4")

                        # Prioridade 1: Mídia explicitamente fixada pelo usuário
                        # Prioridade 2: Auto-seleção do melhor candidato da cena
                        candidate: Optional[MediaCandidate] = None
                        framing_mode = "FILL"

                        if scene.selected_assets and scene.selected_assets[0].media_candidate:
                            sa = scene.selected_assets[0]
                            candidate = sa.media_candidate
                            framing_mode = sa.framing_mode or "FILL"
                        else:
                            # Auto-selecionar o primeiro candidato disponível nas queries da cena
                            for q in scene.queries:
                                if q.media_candidates:
                                    candidate = q.media_candidates[0]
                                    framing_mode = "PAN_AND_ZOOM"
                                    break

                        media_file_path = os.path.join(temp_dir, f"scene_{idx:03d}_media")
                        has_downloaded_media = False

                        if candidate:
                            if candidate.attribution:
                                attributions_set.add(candidate.attribution)

                            raw_url = (
                                candidate.preview_url
                                or candidate.metadata_json.get("file_url")
                                or candidate.url
                            )
                            download_url = RenderService._sanitize_media_url(raw_url)

                            ext = ".jpg"
                            if (
                                candidate.media_type.value == "VIDEO"
                                or "video" in download_url.lower()
                            ):
                                ext = ".mp4"
                            elif download_url.lower().endswith(".png"):
                                ext = ".png"

                            media_file_path += ext

                            try:
                                res = await http_client.get(download_url)
                                if res.status_code == 200 and len(res.content) > 500:
                                    with open(media_file_path, "wb") as mf:  # noqa: ASYNC230
                                        mf.write(res.content)
                                    has_downloaded_media = True
                                    logger.info(
                                        f"Mídia baixada para Cena {scene.position} "
                                        f"({len(res.content)} bytes)"
                                    )
                                else:
                                    logger.warning(
                                        f"Status {res.status_code} ({len(res.content)}B) "
                                        f"ao baixar {download_url}"
                                    )
                            except Exception as dl_err:
                                logger.warning(f"Falha download {download_url}: {dl_err}")

                        # Se não baixou arquivo válido, limpa o path para fallback
                        if not has_downloaded_media:
                            media_file_path = ""

                        VideoComposer.render_scene_clip(
                            media_path=media_file_path,
                            audio_path=audio_path,
                            output_clip_path=clip_path,
                            duration=duration,
                            framing_mode=framing_mode,
                            aspect_ratio=job.aspect_ratio,
                            narration_text=scene.narration,
                        )
                        scene_clips.append(clip_path)

                # 4. Etapa 3: Card de Créditos e Concatenação Final
                job.status = RenderStatus.RENDERING_VIDEO
                job.progress = 80
                await db.commit()

                if job.include_credits_card and attributions_set:
                    credits_clip = os.path.join(temp_dir, "credits_card.mp4")
                    VideoComposer.render_credits_card(
                        attributions=sorted(list(attributions_set)),
                        duration=3.0,
                        output_path=credits_clip,
                        aspect_ratio=job.aspect_ratio,
                    )
                    scene_clips.append(credits_clip)
                    total_duration += 3.0

                # 5. Concatenação em MP4 Full HD final
                final_video_path = str(RenderService.get_rendered_video_path(job_id))
                VideoComposer.concatenate_clips(scene_clips, final_video_path)

                # 6. Concluir job
                job.status = RenderStatus.COMPLETED
                job.progress = 100
                job.duration_seconds = round(total_duration, 2)
                job.video_url = f"/api/v1/render-jobs/{job_id}/stream"
                await db.commit()
                logger.info(f"Vídeo renderizado para Job {job_id} ({total_duration:.1f}s)")

        except Exception as exc:
            logger.error(f"Erro fatal na renderização do Job {job_id}: {exc}", exc_info=True)
            async with session_factory() as db:
                job = await RenderService.get(db, job_id)
                if job:
                    job.status = RenderStatus.FAILED
                    job.error_message = str(exc)
                    await db.commit()
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
