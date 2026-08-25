import pytest

from app.domain.enums import MediaType, QueryType, RightsStatus
from app.domain.schemas import SearchQueryBase
from app.providers.nasa import NASAProvider


@pytest.mark.asyncio
async def test_nasa_provider_direct_search():
    provider = NASAProvider()
    query = SearchQueryBase(
        query="Apollo 11 astronaut lunar moon",
        query_type=QueryType.EVENT,
        priority=1,
    )
    candidates = await provider.search(query, limit=3)
    assert len(candidates) >= 1
    for c in candidates:
        assert c.provider == "nasa"
        assert c.external_id.startswith("nasa-")
        assert c.preview_url
        assert c.rights_status == RightsStatus.SAFE_REUSE
        assert "NASA" in (c.author or "")
        assert c.media_type in [MediaType.IMAGE, MediaType.VIDEO]
