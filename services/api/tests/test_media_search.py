import pytest

from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import SearchQueryBase
from app.providers.pexels import PexelsProvider


@pytest.mark.asyncio
async def test_pexels_provider_direct_search():
    provider = PexelsProvider()
    query = SearchQueryBase(query="datacenter servers broll", priority=1)

    candidates = await provider.search(query, limit=6)
    assert len(candidates) > 0

    for c in candidates:
        assert c.provider == "pexels"
        assert c.rights_status == RightsStatus.SAFE_REUSE
        assert "Pexels" in c.license
        assert c.author is not None
        assert c.preview_url.startswith("http")
        assert c.width is not None and c.width > 0
        assert c.height is not None and c.height > 0
        if c.media_type == MediaType.VIDEO:
            assert c.duration is not None and c.duration > 0


@pytest.mark.asyncio
async def test_search_media_for_query_endpoint(async_client):
    # 1. Create project, scene, and query
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Mídia Teste", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Cena Datacenter", "narration": "Servidores em funcionamento"},
    )
    scene_id = scene_res.json()["id"]

    query_res = await async_client.post(
        f"/api/v1/scenes/{scene_id}/queries",
        json={"query": "data center servers flashing lights broll", "query_type": "BROLL"},
    )
    query_id = query_res.json()["id"]

    # 2. Trigger search
    search_res = await async_client.post(f"/api/v1/queries/{query_id}/search?limit=4")
    assert search_res.status_code == 201
    candidates = search_res.json()
    assert len(candidates) == 4

    candidate = candidates[0]
    assert candidate["rights_status"] in [
        RightsStatus.SAFE_REUSE.value,
        RightsStatus.ATTRIBUTION_REQUIRED.value,
        RightsStatus.REVIEW_REQUIRED.value,
    ]
    assert candidate["provider"] in ["pexels", "wikimedia", "openverse", "nasa"]
    assert "author" in candidate
    assert "preview_url" in candidate

    # 3. List candidates for query
    list_res = await async_client.get(f"/api/v1/queries/{query_id}/candidates")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 4. Get candidate by id
    candidate_id = candidate["id"]
    get_res = await async_client.get(f"/api/v1/candidates/{candidate_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == candidate_id


@pytest.mark.asyncio
async def test_search_media_for_entire_scene(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Projeto Cena Completa",
            "language": "pt-BR",
            "script_raw": "Cena 1:\nVoos cancelados no saguão do aeroporto.",
        },
    )
    project_id = proj_res.json()["id"]

    # Generate scene
    await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")
    scenes_res = await async_client.get(f"/api/v1/projects/{project_id}/scenes")
    scene_id = scenes_res.json()[0]["id"]

    # Generate queries
    await async_client.post(f"/api/v1/scenes/{scene_id}/queries/generate")

    # Search for all scene queries
    scene_search_res = await async_client.post(f"/api/v1/scenes/{scene_id}/search")
    assert scene_search_res.status_code == 201
    candidates = scene_search_res.json()
    assert len(candidates) > 0

    # Verify scene candidates list
    scene_list_res = await async_client.get(f"/api/v1/scenes/{scene_id}/candidates")
    assert scene_list_res.status_code == 200
    assert len(scene_list_res.json()) == len(candidates)
