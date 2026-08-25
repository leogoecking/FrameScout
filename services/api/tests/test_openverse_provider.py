import pytest

from app.domain.enums import QueryType, RightsStatus
from app.domain.schemas import SearchQueryBase
from app.providers.openverse import OpenverseProvider, derive_openverse_rights


def test_derive_openverse_rights_cc0():
    status, lic, attrib = derive_openverse_rights(
        license_code="cc0",
        creator="Museum of Art",
        source="rawpixel",
    )
    assert status == RightsStatus.SAFE_REUSE
    assert "Public Domain" in lic
    assert "Domínio Público via Rawpixel" in attrib


def test_derive_openverse_rights_cc_by():
    status, lic, attrib = derive_openverse_rights(
        license_code="by",
        license_version="2.0",
        creator="John Doe",
        source="flickr",
    )
    assert status == RightsStatus.ATTRIBUTION_REQUIRED
    assert "CC-BY 2.0" in lic
    assert "John Doe" in attrib


@pytest.mark.asyncio
async def test_openverse_provider_direct_search():
    provider = OpenverseProvider()
    query = SearchQueryBase(
        query="Artificial Intelligence technology",
        query_type=QueryType.CONCEPT,
        priority=1,
    )
    candidates = await provider.search(query, limit=3)
    assert len(candidates) >= 1
    for c in candidates:
        assert c.provider == "openverse"
        assert c.external_id.startswith("openverse-")
        assert c.preview_url
        assert c.rights_status in [
            RightsStatus.SAFE_REUSE,
            RightsStatus.ATTRIBUTION_REQUIRED,
            RightsStatus.REVIEW_REQUIRED,
        ]
