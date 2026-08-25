import pytest
from httpx import ASGITransport, AsyncClient

from app.engine.fidelity_engine import FidelityEngine
from app.main import app


def test_fidelity_engine_scoring_high_match():
    # Cenário: Cena fala de CrowdStrike e Tela Azul BSOD em 2024
    score, breakdown = FidelityEngine.calculate_score(
        scene_narration=(
            "Em julho de 2024, uma atualização da CrowdStrike "
            "causou a tela azul da morte no Windows."
        ),
        scene_visual_intent="Monitor exibindo tela azul BSOD com erro fatal do CrowdStrike",
        scene_title="A Pane Global",
        media_title="Windows Blue Screen of Death (BSOD Error) CrowdStrike incident",
        media_provider="wikimedia",
        media_width=1920,
        media_height=1080,
        metadata_json={
            "tags": ["BSOD", "Windows", "CrowdStrike", "outage", "2024"],
            "description": "Tela azul da morte do Windows após incidente do Falcon Sensor em 2024",
        },
    )

    assert score >= 80, f"Score esperado >= 80, obtido {score}"
    assert breakdown["semantic"] > 0
    assert breakdown["entities"] > 0
    assert breakdown["authority"] >= 14.0  # Wikimedia = 0.95 * 15 = 14.25
    assert breakdown["quality"] == 10.0  # 1920x1080 = 1.0 * 10 = 10.0
    assert breakdown["total"] == float(score)


def test_fidelity_engine_broll_match():
    # Cenário: Cena fala de CrowdStrike, mas a mídia é um B-roll genérico de escritório
    score, breakdown = FidelityEngine.calculate_score(
        scene_narration="A pane travou companhias aéreas e hospitais pelo mundo.",
        scene_visual_intent="Monitores e computadores em ambiente corporativo",
        scene_title="O Impacto",
        media_title="Office computers working on desks",
        media_provider="pexels",
        media_width=1920,
        media_height=1080,
        metadata_json={"tags": ["office", "computer", "desk"]},
    )

    # Deve ser um score intermediário (B-Roll) entre 40 e 75
    assert 40 <= score <= 75, f"Score esperado entre 40 e 75 para B-roll, obtido {score}"


def test_fidelity_engine_extract_entities():
    text = "Em 2024, o Falcon Sensor da CrowdStrike provocou um BSOD no Windows 11 em aeroportos."
    entities = FidelityEngine.extract_entities(text)
    assert "crowdstrike" in entities
    assert "bsod" in entities
    assert "falcon" in entities
    assert "windows" in entities


@pytest.mark.asyncio
async def test_rerank_and_metrics_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Criar projeto e cena
        p_res = await client.post(
            "/api/v1/projects",
            json={
                "name": "Projeto Teste Fidelidade",
                "script_raw": "Cena 01: O vazamento de GTA 6 pela Take-Two.",
            },
        )
        assert p_res.status_code == 201
        project_id = p_res.json()["id"]

        scenes_res = await client.post(f"/api/v1/projects/{project_id}/scenes/generate")
        assert scenes_res.status_code == 201
        scene_id = scenes_res.json()[0]["id"]

        # 2. Gerar queries e buscar mídias
        await client.post(f"/api/v1/scenes/{scene_id}/queries/generate")
        search_res = await client.post(f"/api/v1/scenes/{scene_id}/search?limit_per_query=2")
        assert search_res.status_code == 201
        candidates = search_res.json()
        assert len(candidates) > 0
        assert candidates[0]["fidelity_score"] is not None

        # 3. Testar rerank endpoint
        rerank_res = await client.post(f"/api/v1/scenes/{scene_id}/rerank")
        assert rerank_res.status_code == 200
        reranked = rerank_res.json()
        assert len(reranked) == len(candidates)

        # 4. Testar métricas de fidelidade do projeto
        metrics_res = await client.get(f"/api/v1/projects/{project_id}/fidelity-metrics")
        assert metrics_res.status_code == 200
        metrics = metrics_res.json()
        assert "average_fidelity" in metrics
        assert "scenes_covered" in metrics
        assert metrics["total_scenes"] == 1
