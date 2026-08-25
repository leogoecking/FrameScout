import pytest

from app.domain.enums import RightsStatus
from app.domain.schemas import SearchQueryBase
from app.providers.wikimedia import WikimediaProvider, clean_html_tags, derive_rights_status


def test_clean_html_tags_and_unescape():
    raw = '<a href="https://example.com">John &amp; Jane Doe</a> &quot;Photographers&#039;'
    cleaned = clean_html_tags(raw)
    assert cleaned == "John & Jane Doe \"Photographers'"


def test_derive_rights_status_logic():
    # 1. Public domain / CC0 -> SAFE_REUSE
    status, lic, attrib = derive_rights_status("Public domain", credit_text="NASA")
    assert status == RightsStatus.SAFE_REUSE
    assert "Public domain" in lic

    status, _, _ = derive_rights_status("CC0 1.0 Universal")
    assert status == RightsStatus.SAFE_REUSE

    # 2. CC-BY / CC-BY-SA -> ATTRIBUTION_REQUIRED
    status, lic, attrib = derive_rights_status("CC BY-SA 4.0", credit_text="John Doe")
    assert status == RightsStatus.ATTRIBUTION_REQUIRED
    assert "CC BY-SA 4.0" in lic
    assert "John Doe" in attrib
    assert "Wikimedia Commons" in attrib

    status, lic, _ = derive_rights_status("CC BY 3.0", credit_text="Jane Smith")
    assert status == RightsStatus.ATTRIBUTION_REQUIRED

    # 3. Non-Commercial / Fair use / Restricted -> REVIEW_REQUIRED
    status, lic, _ = derive_rights_status("CC BY-NC 4.0", credit_text="Artist")
    assert status == RightsStatus.REVIEW_REQUIRED

    status, lic, _ = derive_rights_status("CC BY-NC-SA 2.0", credit_text="Artist")
    assert status == RightsStatus.REVIEW_REQUIRED

    status, lic, _ = derive_rights_status("Fair use / Trademark")
    assert status == RightsStatus.REVIEW_REQUIRED

    status, lic, _ = derive_rights_status(None)
    assert status == RightsStatus.REVIEW_REQUIRED


@pytest.mark.asyncio
async def test_wikimedia_provider_direct_search():
    provider = WikimediaProvider()
    query = SearchQueryBase(query="CrowdStrike logo official", priority=1)

    candidates = await provider.search(query, limit=5)
    assert len(candidates) > 0

    for c in candidates:
        assert c.provider == "wikimedia"
        assert c.rights_status in [
            RightsStatus.SAFE_REUSE,
            RightsStatus.ATTRIBUTION_REQUIRED,
            RightsStatus.REVIEW_REQUIRED,
        ]
        assert c.author is not None
        assert c.preview_url.startswith("http")
        assert c.width is not None and c.width > 0
        assert c.height is not None and c.height > 0
        assert c.attribution is not None


@pytest.mark.asyncio
async def test_search_media_with_provider_filter(async_client):
    proj_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Projeto Wikimedia Teste", "language": "pt-BR"},
    )
    project_id = proj_res.json()["id"]

    scene_res = await async_client.post(
        f"/api/v1/projects/{project_id}/scenes",
        json={"title": "Cena GTA", "narration": "Take-Two investiga o vazamento"},
    )
    scene_id = scene_res.json()["id"]

    query_res = await async_client.post(
        f"/api/v1/scenes/{scene_id}/queries",
        json={"query": "Take-Two Interactive official", "query_type": "OFFICIAL"},
    )
    query_id = query_res.json()["id"]

    # 1. Search specifically in Wikimedia
    wiki_res = await async_client.post(
        f"/api/v1/queries/{query_id}/search?provider=wikimedia&limit=4"
    )
    assert wiki_res.status_code == 201
    wiki_candidates = wiki_res.json()
    assert len(wiki_candidates) > 0
    assert all(c["provider"] == "wikimedia" for c in wiki_candidates)

    # 2. Search multi-provider in scene
    scene_res = await async_client.post(f"/api/v1/scenes/{scene_id}/search")
    assert scene_res.status_code == 201
    all_candidates = scene_res.json()
    assert len(all_candidates) > 0
