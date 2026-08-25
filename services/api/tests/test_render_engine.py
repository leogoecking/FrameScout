import pytest

from app.domain.enums import RenderStatus
from app.engine.tts_engine import TTSEngine
from app.engine.video_composer import VideoComposer


def test_tts_engine_voice_catalog():
    voices = TTSEngine.list_voices()
    assert len(voices) >= 3
    assert any(v["id"] == "pt-BR-AntonioNeural" for v in voices)
    assert any(v["id"] == "pt-BR-FranciscaNeural" for v in voices)


def test_video_composer_dimensions():
    w169, h169 = VideoComposer.get_dimensions("16:9")
    assert w169 == 1920
    assert h169 == 1080

    w916, h916 = VideoComposer.get_dimensions("9:16")
    assert w916 == 1080
    assert h916 == 1920


@pytest.mark.asyncio
async def test_trigger_render_job_endpoint(async_client):
    # 1. Create project
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Documentário CrowdStrike Studio",
            "language": "pt-BR",
            "script_raw": "Cena 1:\nFalha no sistema global.",
        },
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # Generate scenes
    await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")

    # 2. Trigger render job
    render_res = await async_client.post(
        f"/api/v1/projects/{project_id}/render",
        json={
            "aspect_ratio": "16:9",
            "voice": "pt-BR-AntonioNeural",
            "include_subtitles": True,
            "include_credits_card": True,
        },
    )
    assert render_res.status_code == 201
    job_data = render_res.json()
    assert job_data["project_id"] == project_id
    assert job_data["status"] in [
        RenderStatus.PENDING.value,
        RenderStatus.SYNTHESIZING_AUDIO.value,
        RenderStatus.PROCESSING_MEDIA.value,
        RenderStatus.RENDERING_VIDEO.value,
        RenderStatus.COMPLETED.value,
    ]
    job_id = job_data["id"]

    # 3. Query render job status
    status_res = await async_client.get(f"/api/v1/render-jobs/{job_id}")
    assert status_res.status_code == 200
    assert status_res.json()["id"] == job_id
