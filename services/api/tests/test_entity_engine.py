import pytest

from app.domain.enums import EntityCategory, QueryType
from app.engine.entity_engine import EntityEngine


def test_entity_extraction_gtavi_leak():
    text = (
        "A Take-Two e a Rockstar Games abriram um processo judicial "
        "para investigar o vazamento de GTA VI ocorrido em setembro de 2022."
    )
    entities = EntityEngine.extract_entities(text)
    assert len(entities) >= 4

    categories = {e.category for e in entities}
    assert EntityCategory.ORGANIZATION in categories
    assert EntityCategory.PRODUCT in categories
    assert EntityCategory.EVENT in categories
    assert EntityCategory.DATE_TIME in categories

    texts = [e.text.lower() for e in entities]
    assert any("take-two" in t or "take two" in t for t in texts)
    assert any("rockstar" in t for t in texts)
    assert any("gta vi" in t or "gta" in t for t in texts)
    assert any("vazamento" in t or "processo" in t for t in texts)
    assert any("setembro de 2022" in t for t in texts)


def test_entity_extraction_crowdstrike_outage():
    text = (
        "Em 19 de julho de 2024, uma atualização do Falcon Sensor da CrowdStrike "
        "causou a tela azul da morte (BSOD) em milhões de computadores Windows da Microsoft, "
        "travando aeroportos nos Estados Unidos."
    )
    entities = EntityEngine.extract_entities(text)
    assert len(entities) >= 5

    categories = {e.category for e in entities}
    assert EntityCategory.DATE_TIME in categories
    assert EntityCategory.ORGANIZATION in categories
    assert EntityCategory.PRODUCT in categories
    assert EntityCategory.TECHNOLOGY in categories
    assert EntityCategory.LOCATION in categories

    texts = [e.text.lower() for e in entities]
    assert any("19 de julho de 2024" in t for t in texts)
    assert any("crowdstrike" in t for t in texts)
    assert any("microsoft" in t for t in texts)
    assert any("falcon" in t for t in texts)
    assert any("windows" in t for t in texts)
    assert any("bsod" in t or "tela azul" in t for t in texts)
    assert any("estados unidos" in t for t in texts)


def test_entity_extraction_nasa_space():
    text = (
        "O telescópio James Webb da NASA capturou fotos inéditas no espaço "
        "enquanto o rover Perseverance explorava a superfície de Marte."
    )
    entities = EntityEngine.extract_entities(text)
    assert len(entities) >= 3

    categories = {e.category for e in entities}
    assert EntityCategory.ORGANIZATION in categories
    assert EntityCategory.PRODUCT in categories
    assert EntityCategory.LOCATION in categories

    texts = [e.text.lower() for e in entities]
    assert any("nasa" in t for t in texts)
    assert any("james webb" in t for t in texts)
    assert any("marte" in t for t in texts)


def test_entity_extraction_ai_regulation_and_person():
    text = (
        "O Senado Federal debateu o PL 2.338 sobre Inteligência Artificial "
        "com Sam Altman no Brasil."
    )
    entities = EntityEngine.extract_entities(text)
    assert len(entities) >= 4

    categories = {e.category for e in entities}
    assert EntityCategory.ORGANIZATION in categories
    assert EntityCategory.EVENT in categories
    assert EntityCategory.TECHNOLOGY in categories
    assert EntityCategory.PERSON in categories
    assert EntityCategory.LOCATION in categories

    texts = [e.text.lower() for e in entities]
    assert any("senado federal" in t or "senado" in t for t in texts)
    assert any("pl 2.338" in t for t in texts)
    assert any("inteligência artificial" in t for t in texts)
    assert any("sam altman" in t for t in texts)
    assert any("brasil" in t for t in texts)


def test_generate_queries_from_entities():
    text = "A CrowdStrike lançou atualização do Falcon Sensor causando apagão global na nuvem."
    entities = EntityEngine.extract_entities(text)
    queries = EntityEngine.generate_queries_from_entities(entities, scene_title="Falha Global")

    assert len(queries) >= 3
    q_types = {q.query_type for q in queries}
    assert QueryType.OFFICIAL in q_types
    assert QueryType.EVENT in q_types
    assert QueryType.BROLL in q_types


@pytest.mark.asyncio
async def test_scene_and_project_entity_endpoints(async_client):
    # 1. Create project with script
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={
            "name": "Projeto NER Teste",
            "script_raw": (
                "Cena 01: Em julho de 2024, a CrowdStrike causou uma pane "
                "no Windows da Microsoft.\n\n"
                "Cena 02: A NASA utilizou o telescópio James Webb para "
                "investigar o espaço profundo."
            ),
        },
    )
    assert proj_res.status_code == 201
    project_id = proj_res.json()["id"]

    # 2. Generate scenes
    scenes_res = await async_client.post(f"/api/v1/projects/{project_id}/scenes/generate")
    assert scenes_res.status_code == 201
    scenes = scenes_res.json()
    assert len(scenes) == 2
    scene_1_id = scenes[0]["id"]

    # 3. Test Scene Entity Extract Endpoint
    sc_res = await async_client.post(f"/api/v1/scenes/{scene_1_id}/entities/extract")
    assert sc_res.status_code == 200
    sc_data = sc_res.json()
    assert sc_data["scene_id"] == scene_1_id
    assert len(sc_data["entities"]) > 0
    assert len(sc_data["suggested_queries"]) > 0

    # 4. Test Project Entity Extract Endpoint
    proj_ent_res = await async_client.post(f"/api/v1/projects/{project_id}/entities/extract")
    assert proj_ent_res.status_code == 200
    p_data = proj_ent_res.json()
    assert p_data["project_id"] == project_id
    assert p_data["total_entities_count"] > 0
    assert "ORGANIZATION" in p_data["entities_by_category"]
    assert len(p_data["scenes_entities"]) == 2
