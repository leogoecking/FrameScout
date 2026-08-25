import pytest


@pytest.mark.asyncio
async def test_create_project(async_client):
    payload = {
        "name": "Documentário CrowdStrike",
        "language": "pt-BR",
        "script_raw": "Em julho de 2024, uma falha global afetou milhões de computadores.",
    }
    response = await async_client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["language"] == payload["language"]
    assert data["script_raw"] == payload["script_raw"]
    assert "id" in data
    assert data["scenes_count"] == 0


@pytest.mark.asyncio
async def test_list_projects(async_client):
    # Create two projects
    await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Alpha", "language": "pt-BR", "script_raw": "Roteiro A"},
    )
    await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Beta", "language": "en-US", "script_raw": "Script B"},
    )

    response = await async_client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    names = [p["name"] for p in data]
    assert "Projeto Alpha" in names
    assert "Projeto Beta" in names


@pytest.mark.asyncio
async def test_get_project_by_id(async_client):
    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Específico", "language": "es-ES", "script_raw": "Texto"},
    )
    project_id = create_res.json()["id"]

    get_res = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == project_id
    assert data["name"] == "Projeto Específico"
    assert data["language"] == "es-ES"


@pytest.mark.asyncio
async def test_get_project_not_found(async_client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await async_client.get(f"/api/v1/projects/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Projeto não encontrado"


@pytest.mark.asyncio
async def test_update_project_and_script(async_client):
    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Nome Original", "language": "pt-BR", "script_raw": "Versão 1"},
    )
    project_id = create_res.json()["id"]

    update_payload = {
        "name": "Nome Atualizado",
        "script_raw": "Versão 2 revisada do roteiro completo.",
    }
    put_res = await async_client.put(f"/api/v1/projects/{project_id}", json=update_payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert data["name"] == "Nome Atualizado"
    assert data["script_raw"] == "Versão 2 revisada do roteiro completo."
    assert data["language"] == "pt-BR"


@pytest.mark.asyncio
async def test_delete_project(async_client):
    create_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Para Deletar", "language": "pt-BR"},
    )
    project_id = create_res.json()["id"]

    del_res = await async_client.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    # Verify 404 on subsequent get
    get_res = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404
