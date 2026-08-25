import pytest

from app.domain.enums import QueryType


@pytest.mark.asyncio
async def test_generate_queries_for_scene_gta_example(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Documentário GTA VI", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={
            "title": "O Vazamento",
            "narration": "Take-Two tenta identificar o responsável pelo vazamento de GTA VI.",
            "visual_intent": "gaming leak investigation broll",
        },
    )
    scene_id = scene_res.json()["id"]

    gen_res = await async_client.post(f"/api/v1/scenes/{scene_id}/queries/generate")
    assert gen_res.status_code == 201
    queries = gen_res.json()
    assert len(queries) >= 3

    types = [q["query_type"] for q in queries]
    assert QueryType.EVENT.value in types
    assert QueryType.OFFICIAL.value in types or QueryType.COMPANY.value in types
    assert QueryType.BROLL.value in types

    all_query_strings = " ".join(q["query"] for q in queries)
    assert "Take-Two" in all_query_strings
    assert "GTA" in all_query_strings


@pytest.mark.asyncio
async def test_generate_queries_for_crowdstrike_scene(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "CrowdStrike Doc", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={
            "title": "A Queda dos Sistemas",
            "narration": "A CrowdStrike causou uma pane global nos sistemas Windows.",
            "visual_intent": "B-roll de tela azul da morte ou servidores em pane",
        },
    )
    scene_id = scene_res.json()["id"]

    gen_res = await async_client.post(f"/api/v1/scenes/{scene_id}/queries/generate")
    assert gen_res.status_code == 201
    queries = gen_res.json()
    assert len(queries) >= 3

    all_query_strings = " ".join(q["query"] for q in queries)
    assert "CrowdStrike" in all_query_strings


@pytest.mark.asyncio
async def test_batch_generate_project_queries(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Projeto Batch",
            "language": "pt-BR",
            "script_raw": "Cena 1:\nTexto da primeira cena.\n\nCena 2:\nTexto da segunda cena.",
        },
    )
    project_id = proj_res.json()["id"]

    await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")

    batch_res = await async_client.post(f"/api/v1/projects/{project_id}/queries/generate")
    assert batch_res.status_code == 201
    data = batch_res.json()
    assert data["scenes_count"] == 2
    assert data["total_queries_created"] >= 4


@pytest.mark.asyncio
async def test_crud_manual_search_queries(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto CRUD Queries", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Cena Teste", "narration": "Texto teste"},
    )
    scene_id = scene_res.json()["id"]

    # Create manual query (testing case-insensitivity)
    create_res = await async_client.post(
        f"/api/v1/scenes/{scene_id}/queries",
        json={
            "query": "datacenter server room 4k footage",
            "query_type": "broll",
            "priority": 1,
        },
    )
    assert create_res.status_code == 201
    query_id = create_res.json()["id"]
    assert create_res.json()["query"] == "datacenter server room 4k footage"
    assert create_res.json()["query_type"] == "BROLL"

    # List queries
    list_res = await async_client.get(f"/api/v1/scenes/{scene_id}/queries")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Update query
    update_res = await async_client.put(
        f"/api/v1/queries/{query_id}",
        json={"query": "datacenter server rack flashing lights", "priority": 2},
    )
    assert update_res.status_code == 200
    assert update_res.json()["query"] == "datacenter server rack flashing lights"
    assert update_res.json()["priority"] == 2

    # Delete query
    del_res = await async_client.delete(f"/api/v1/queries/{query_id}")
    assert del_res.status_code == 204

    # Verify empty
    list_res_after = await async_client.get(f"/api/v1/scenes/{scene_id}/queries")
    assert len(list_res_after.json()) == 0
