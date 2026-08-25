from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import MediaCandidateBase, ProjectCreate, SceneBase


def test_rights_status_enum_values():
    assert RightsStatus.SAFE_REUSE == "SAFE_REUSE"
    assert RightsStatus.ATTRIBUTION_REQUIRED == "ATTRIBUTION_REQUIRED"
    assert RightsStatus.REVIEW_REQUIRED == "REVIEW_REQUIRED"
    assert RightsStatus.REFERENCE_ONLY == "REFERENCE_ONLY"
    assert RightsStatus.BLOCKED == "BLOCKED"


def test_project_create_schema():
    p = ProjectCreate(name="Novo Documentário", language="pt-BR", script_raw="Texto do roteiro")
    assert p.name == "Novo Documentário"
    assert p.language == "pt-BR"
    assert p.script_raw == "Texto do roteiro"


def test_scene_schema():
    s = SceneBase(position=1, narration="Cena inicial", visual_intent="B-roll de servidores")
    assert s.position == 1
    assert s.narration == "Cena inicial"
    assert s.visual_intent == "B-roll de servidores"


def test_media_candidate_defaults_to_review_required():
    m = MediaCandidateBase(
        provider="pexels",
        external_id="12345",
        url="https://pexels.com/12345",
        preview_url="https://pexels.com/12345-thumb.jpg",
        media_type=MediaType.IMAGE,
    )
    assert m.rights_status == RightsStatus.REVIEW_REQUIRED
