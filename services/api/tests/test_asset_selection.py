import pytest


@pytest.mark.asyncio
async def test_asset_selection_and_visual_plan_export(async_client):
    # 1. Create project with scenes and queries
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Documentário CrowdStrike 2024",
            "language": "pt-BR",
            "script_raw": (
                "Cena 1:\nEm 19 de julho de 2024, atualização causou tela azul global.\n\n"
                "Cena 2:\nAeroportos paralisaram voos no mundo inteiro."
            ),
        },
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # Generate scenes
    gen_res = await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")
    assert gen_res.status_code == 201
    scenes = gen_res.json()
    assert len(scenes) == 2
    scene_1_id = scenes[0]["id"]
    scene_2_id = scenes[1]["id"]

    # Generate queries
    await async_client.post(f"/api/v1/scenes/{scene_1_id}/queries/generate")
    await async_client.post(f"/api/v1/scenes/{scene_2_id}/queries/generate")

    # Search media for scene 1 (Wikimedia) and scene 2 (Pexels)
    search_1 = await async_client.post(f"/api/v1/scenes/{scene_1_id}/search?provider=wikimedia")
    assert search_1.status_code == 201
    cands_scene_1 = search_1.json()
    assert len(cands_scene_1) > 0

    search_2 = await async_client.post(f"/api/v1/scenes/{scene_2_id}/search?provider=pexels")
    assert search_2.status_code == 201
    cands_scene_2 = search_2.json()
    assert len(cands_scene_2) > 0

    # 2. Select asset for Scene 1
    selected_cand_1 = cands_scene_1[0]
    select_res_1 = await async_client.post(
        f"/api/v1/scenes/{scene_1_id}/assets/select",
        json={
            "media_candidate_id": selected_cand_1["id"],
            "framing_mode": "PAN_AND_ZOOM",
            "notes": "Efeito Ken Burns suave sobre a imagem",
        },
    )
    assert select_res_1.status_code == 201
    asset_1 = select_res_1.json()
    assert asset_1["framing_mode"] == "PAN_AND_ZOOM"
    assert asset_1["notes"] == "Efeito Ken Burns suave sobre a imagem"
    assert asset_1["media_candidate"]["id"] == selected_cand_1["id"]

    # 3. Select asset for Scene 2
    selected_cand_2 = cands_scene_2[0]
    select_res_2 = await async_client.post(
        f"/api/v1/scenes/{scene_2_id}/assets/select",
        json={
            "media_candidate_id": selected_cand_2["id"],
            "framing_mode": "FILL",
        },
    )
    assert select_res_2.status_code == 201
    asset_2 = select_res_2.json()
    assert asset_2["framing_mode"] == "FILL"

    # 4. Update asset 1 framing mode
    update_res = await async_client.put(
        f"/api/v1/selected-assets/{asset_1['id']}",
        json={"framing_mode": "FIT", "notes": "Ajustado para proporção original"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["framing_mode"] == "FIT"

    # 5. List scene 1 assets
    list_res = await async_client.get(f"/api/v1/scenes/{scene_1_id}/assets")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 6. Export Visual Plan
    plan_res = await async_client.get(f"/api/v1/projects/{project_id}/visual-plan")
    assert plan_res.status_code == 200
    plan_data = plan_res.json()

    assert plan_data["total_scenes"] == 2
    assert plan_data["covered_scenes_count"] == 2
    assert len(plan_data["scenes"]) == 2
    assert len(plan_data["consolidated_attributions"]) > 0
    assert "Plano de Produção Visual" in plan_data["markdown_document"]
    assert "Créditos e Atribuições Consolidadas" in plan_data["markdown_document"]
    assert "Cena 01" in plan_data["markdown_document"]
    assert "Cena 02" in plan_data["markdown_document"]
