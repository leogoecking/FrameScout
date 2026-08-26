import pytest

from app.domain.enums import ScriptTone
from app.engine.script_engine import ScriptEngine


@pytest.mark.asyncio
async def test_script_engine_direct_generation():
    response = await ScriptEngine.generate_script(
        topic="A História da GPU e o Avanço dos Games",
        tone=ScriptTone.DOCUMENTARY,
        target_duration="3m",
    )
    assert response.title is not None
    assert response.word_count > 40
    assert response.estimated_duration_seconds >= 30
    assert "Cena 01:" in response.script_raw
    assert "Cena 02:" in response.script_raw
    assert response.tone == ScriptTone.DOCUMENTARY


@pytest.mark.asyncio
async def test_script_engine_shorts_generation():
    response = await ScriptEngine.generate_script(
        topic="Por que a CrowdStrike parou o mundo em 2024",
        tone=ScriptTone.VIRAL_SHORTS,
        target_duration="60s",
    )
    assert response.topic == "Por que a CrowdStrike parou o mundo em 2024"
    assert response.tone == ScriptTone.VIRAL_SHORTS
    assert "Cena 01:" in response.script_raw
    assert response.word_count > 30


@pytest.mark.asyncio
async def test_generate_script_endpoints(async_client):
    # 1. Standalone Script Generation Endpoint
    gen_res = await async_client.post(
        "/api/v1/projects/generate-script",
        json={
            "topic": "A Corrida Espacial e o Telescópio James Webb",
            "tone": "EXPLAINER",
            "target_duration": "3m",
        },
    )
    assert gen_res.status_code == 200
    data = gen_res.json()
    assert "James Webb" in data["topic"]
    assert "Cena 01:" in data["script_raw"]
    assert data["tone"] == "EXPLAINER"

    # 2. Project Script Generation & Auto Scene Generation
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Roteiro IA", "language": "pt-BR"},
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    apply_res = await async_client.post(
        f"/api/v1/projects/{project_id}/generate-script",
        json={
            "topic": "O colapso da CrowdStrike no Windows",
            "tone": "DOCUMENTARY",
            "target_duration": "3m",
            "auto_generate_scenes": True,
        },
    )
    assert apply_res.status_code == 200
    script_data = apply_res.json()
    assert "Cena 01:" in script_data["script_raw"]

    # 3. Verify scenes were automatically created from the generated script
    scenes_res = await async_client.get(f"/api/v1/projects/{project_id}/scenes")
    assert scenes_res.status_code == 200
    scenes = scenes_res.json()
    assert len(scenes) >= 2
    assert scenes[0]["position"] == 1
