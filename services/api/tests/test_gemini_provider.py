import pytest

from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import SearchQueryBase
from app.providers.gemini_imagen import GeminiImagenProvider


@pytest.mark.asyncio
async def test_gemini_provider_direct_generation():
    provider = GeminiImagenProvider()
    query = SearchQueryBase(
        query="Futuristic quantum datacenter with glowing neural processors",
        priority=1,
    )
    candidates = await provider.search(query, limit=2)
    assert len(candidates) == 2

    for c in candidates:
        assert c.provider == "gemini"
        assert c.media_type == MediaType.IMAGE
        assert c.rights_status == RightsStatus.SAFE_REUSE
        assert "Imagen" in c.author or "Gemini" in c.author
        assert c.width == 1920
        assert c.height == 1080
        assert c.metadata_json is not None
        assert c.metadata_json.get("ai_generated") is True


@pytest.mark.asyncio
async def test_gemini_provider_aspect_ratio_portrait():
    provider = GeminiImagenProvider()
    candidates = await provider.generate_image(
        prompt="Cyberpunk neon city street vertical shot",
        aspect_ratio="9:16",
        sample_count=1,
    )
    assert len(candidates) == 1
    c = candidates[0]
    assert c.width == 1080
    assert c.height == 1920
    assert c.rights_status == RightsStatus.SAFE_REUSE


@pytest.mark.asyncio
async def test_generate_scene_ai_image_endpoint(async_client):
    # 1. Create project & scene
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Projeto AI Imagen Teste",
            "script_raw": (
                "Cena 01: O futuro da computação quântica e processadores de 2 nanômetros."
            ),
        },
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    scenes_res = await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")
    assert scenes_res.status_code == 201
    scenes = scenes_res.json()
    assert len(scenes) == 1
    scene_id = scenes[0]["id"]

    # 2. Trigger AI Image Generation for Scene
    ai_gen_res = await async_client.post(
        f"/api/v1/scenes/{scene_id}/ai/generate-image",
        json={
            "prompt": "Microprocessador quântico de 2nm com circuitos brilhantes",
            "aspect_ratio": "16:9",
            "count": 2,
        },
    )
    assert ai_gen_res.status_code == 201
    ai_cands = ai_gen_res.json()
    assert len(ai_cands) == 2
    for cand in ai_cands:
        assert cand["provider"] == "gemini"
        assert cand["rights_status"] == "SAFE_REUSE"
        assert cand["media_type"] == "IMAGE"
        assert cand["metadata_json"]["ai_generated"] is True

    # 3. Verify candidates are listed in the scene
    scene_cands_res = await async_client.get(f"/api/v1/scenes/{scene_id}/candidates")
    assert scene_cands_res.status_code == 200
    listed_cands = scene_cands_res.json()
    assert len(listed_cands) >= 2
    assert any(c["provider"] == "gemini" for c in listed_cands)
