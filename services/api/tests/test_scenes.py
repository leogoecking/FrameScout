import pytest


@pytest.mark.asyncio
async def test_generate_scenes_from_script(async_client):
    # 1. Create project with structured script
    script = """
    Cena 1: A Pane Global
    Em 19 de julho de 2024, uma atualização da CrowdStrike provocou uma interrupção de TI.

    Cena 2: O Caos nos Aeroportos
    Voos foram cancelados em massa, painéis apagaram e passageiros lotaram saguões.

    Cena 3: Hospitais e Bancos
    Sistemas hospitalares paralisaram e caixas eletrônicos exibiram a tela azul da morte.
    """
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Documentário CrowdStrike", "language": "pt-BR", "script_raw": script},
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 2. Trigger automatic generation
    gen_res = await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")
    assert gen_res.status_code == 201
    scenes = gen_res.json()
    assert len(scenes) == 3

    assert scenes[0]["position"] == 1
    assert "A Pane Global" in scenes[0]["title"]
    assert "CrowdStrike" in scenes[0]["narration"]
    assert scenes[0]["start_estimate"] == 0.0
    assert scenes[0]["end_estimate"] > 0.0

    assert scenes[1]["position"] == 2
    assert "Aeroportos" in scenes[1]["title"]
    assert scenes[1]["start_estimate"] == scenes[0]["end_estimate"]

    assert scenes[2]["position"] == 3
    assert "Hospitais" in scenes[2]["title"]


@pytest.mark.asyncio
async def test_create_and_list_scenes_manually(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Cenas Manuais", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    # Create Scene 1
    s1_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Introdução", "narration": "Texto da primeira cena."},
    )
    assert s1_res.status_code == 201
    assert s1_res.json()["position"] == 1

    # Create Scene 2
    s2_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Desenvolvimento", "narration": "Texto da segunda cena."},
    )
    assert s2_res.status_code == 201
    assert s2_res.json()["position"] == 2

    # List
    list_res = await async_client.get(f"/api/v1/projects/{project_id}/scenes")
    assert list_res.status_code == 200
    scenes = list_res.json()
    assert len(scenes) == 2
    assert scenes[0]["title"] == "Introdução"
    assert scenes[1]["title"] == "Desenvolvimento"


@pytest.mark.asyncio
async def test_update_scene(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Update", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    create_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Original", "narration": "Narração inicial."},
    )
    scene_id = create_res.json()["id"]

    update_res = await async_client.put(
        f"/api/v1/scenes/{scene_id}",
        json={
            "title": "Título Modificado",
            "visual_intent": "B-roll específico de datacenter",
        },
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["title"] == "Título Modificado"
    assert data["visual_intent"] == "B-roll específico de datacenter"


@pytest.mark.asyncio
async def test_reorder_scenes(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Reorder", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    s1 = (
        await async_client.post(
            f"/api/v1/projects/{project_id}/scenes",
            json={"title": "Cena 1", "narration": "Primeira"},
        )
    ).json()

    s2 = (
        await async_client.post(
            f"/api/v1/projects/{project_id}/scenes",
            json={"title": "Cena 2", "narration": "Segunda"},
        )
    ).json()

    # Reorder s2, s1
    reorder_res = await async_client.put(
        f"/api/v1/projects/{project_id}/scenes/reorder",
        json={"scene_ids": [s2["id"], s1["id"]]},
    )
    assert reorder_res.status_code == 200
    reordered = reorder_res.json()
    assert reordered[0]["id"] == s2["id"]
    assert reordered[0]["position"] == 1
    assert reordered[1]["id"] == s1["id"]
    assert reordered[1]["position"] == 2


@pytest.mark.asyncio
async def test_split_and_merge_scenes(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Split Merge", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene = (
        await async_client.post(
            f"/api/v1/projects/{project_id}/scenes",
            json={"title": "Cena Longa", "narration": "Parte 1 do texto. Parte 2 do texto."},
        )
    ).json()
    scene_id = scene["id"]

    # Split
    split_res = await async_client.post(
        f"/api/v1/scenes/{scene_id}/split",
        json={
            "first_part_narration": "Parte 1 do texto.",
            "second_part_narration": "Parte 2 do texto.",
            "first_part_title": "Cena 01 - Parte A",
            "second_part_title": "Cena 02 - Parte B",
        },
    )
    assert split_res.status_code == 200
    split_scenes = split_res.json()
    assert len(split_scenes) == 2
    assert split_scenes[0]["title"] == "Cena 01 - Parte A"
    assert split_scenes[1]["title"] == "Cena 02 - Parte B"
    assert split_scenes[1]["position"] == 2

    # Merge them back
    merge_res = await async_client.post(
        f"/api/v1/scenes/{split_scenes[0]['id']}/merge",
        json={"target_scene_id": split_scenes[1]["id"]},
    )
    assert merge_res.status_code == 200
    merged = merge_res.json()
    assert "Parte 1" in merged["narration"]
    assert "Parte 2" in merged["narration"]

    # Verify only 1 scene remains in project
    list_res = await async_client.get(f"/api/v1/projects/{project_id}/scenes")
    assert len(list_res.json()) == 1
