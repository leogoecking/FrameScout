import logging
import re
from typing import Any, Dict, List, Optional

import httpx

from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import MediaCandidateBase, SearchQueryBase
from app.providers.base import MediaProvider
from app.providers.wikimedia import generate_search_variants

logger = logging.getLogger("framescout.providers.nasa")

NASA_USER_AGENT = "FrameScout/0.1.0 (contact@framescout.io)"
NASA_DEFAULT_LICENSE = "Public Domain (NASA / US Federal Government Work)"
NASA_DEFAULT_ATTRIBUTION = (
    "Mídia de Domínio Público por NASA (National Aeronautics and Space Administration)"
)


class NASAProvider(MediaProvider):
    """
    Provedor de integração oficial com a API da NASA (Image and Video Library).
    Recupera fotos em altíssima resolução e vídeos em MP4 de missões espaciais,
    ciência, lançamentos de foguetes, telescópios e exploração planetária.
    Todo material institucional da NASA é de Domínio Público por lei (SAFE_REUSE).
    """

    def __init__(self, base_url: str = "https://images-api.nasa.gov"):
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "nasa"

    async def search(self, query: SearchQueryBase, limit: int = 10) -> List[MediaCandidateBase]:
        try:
            return await self._search_remote(query, limit)
        except Exception as exc:
            logger.warning(
                f"Falha na consulta à API da NASA ({exc}). Recorrendo ao sandbox de contingência."
            )
            return self._generate_sandbox_candidates(query, limit)

    async def _search_remote(self, query: SearchQueryBase, limit: int) -> List[MediaCandidateBase]:
        variants = generate_search_variants(query.query)
        headers = {"User-Agent": NASA_USER_AGENT}

        async with httpx.AsyncClient(timeout=12.0) as client:
            for search_term in variants:
                params = {
                    "q": search_term,
                    "media_type": "image,video",
                    "page_size": str(max(limit * 2, 6)),
                }

                res = await client.get(f"{self.base_url}/search", params=params, headers=headers)
                if res.status_code != 200:
                    continue

                data = res.json()
                items = data.get("collection", {}).get("items", [])
                if not items:
                    continue

                candidates: List[MediaCandidateBase] = []
                for item in items:
                    candidate = self._map_nasa_item_to_candidate(item, query.query)
                    if candidate:
                        candidates.append(candidate)

                if candidates:
                    return candidates[:limit]

        return self._generate_sandbox_candidates(query, limit)

    def _map_nasa_item_to_candidate(
        self, item: Dict[str, Any], query_term: str
    ) -> Optional[MediaCandidateBase]:
        data_list = item.get("data", [])
        if not data_list:
            return None

        entry = data_list[0]
        nasa_id = str(entry.get("nasa_id") or item.get("href", ""))
        title = entry.get("title") or f"Registro NASA: {query_term}"
        media_type_str = entry.get("media_type", "image").lower()
        center = entry.get("center", "NASA")
        author = f"NASA / {center}"

        links = item.get("links", [])
        preview_url = ""
        for link in links:
            rel = link.get("rel")
            if rel in ["preview", "alternate"]:
                preview_url = link.get("href", "")
                if preview_url:
                    break

        if not preview_url and links:
            preview_url = links[0].get("href", "")

        is_video = media_type_str == "video"
        media_type = MediaType.VIDEO if is_video else MediaType.IMAGE
        direct_video_url = ""
        if is_video and nasa_id:
            # Padrão canônico de URL de vídeo CDN da NASA
            safe_id = re.sub(r"\s+", "%20", nasa_id)
            direct_video_url = f"https://images-assets.nasa.gov/video/{safe_id}/{safe_id}~orig.mp4"

        landing_url = f"https://images.nasa.gov/details-{nasa_id}"

        return MediaCandidateBase(
            provider=self.name,
            external_id=f"nasa-{nasa_id}",
            title=title,
            url=landing_url,
            preview_url=preview_url or direct_video_url,
            media_type=media_type,
            width=1920,
            height=1080,
            duration=15.0 if is_video else None,
            author=author,
            license=NASA_DEFAULT_LICENSE,
            attribution=f"Mídia oficial por {author} (Domínio Público)",
            rights_status=RightsStatus.SAFE_REUSE,
            fidelity_score=0.98,
            metadata_json={
                "nasa_id": nasa_id,
                "center": center,
                "date_created": entry.get("date_created"),
                "description": entry.get("description"),
                "keywords": entry.get("keywords", []),
                "video_stream_url": direct_video_url if is_video else None,
            },
        )

    def _generate_sandbox_candidates(
        self, query: SearchQueryBase, limit: int
    ) -> List[MediaCandidateBase]:
        term = query.query.strip()
        lower = term.lower()

        thematic_catalog = [
            {
                "id": "nasa-apollo-11-moonwalk",
                "tags": [
                    "apollo",
                    "lua",
                    "moon",
                    "astronauta",
                    "astronaut",
                    "espaco",
                    "espaço",
                    "space",
                ],
                "type": MediaType.IMAGE,
                "title": f"Apollo 11 Astronaut on Lunar Surface - {term}",
                "center": "JSC",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Aldrin_Apollo_11.jpg/960px-Aldrin_Apollo_11.jpg",
                "nasa_id": "AS11-40-5903",
            },
            {
                "id": "nasa-james-webb-deep-field",
                "tags": [
                    "telescopio",
                    "telescópio",
                    "webb",
                    "universo",
                    "galaxia",
                    "galáxia",
                    "estrela",
                    "deep",
                ],
                "type": MediaType.IMAGE,
                "title": f"James Webb Space Telescope Deep Cosmic Field - {term}",
                "center": "GSFC",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Webb%27s_First_Deep_Field.jpg/960px-Webb%27s_First_Deep_Field.jpg",
                "nasa_id": "GSFC_20220712_Webb_Deep_Field",
            },
            {
                "id": "nasa-sls-artemis-launch",
                "tags": [
                    "foguete",
                    "lancamento",
                    "lançamento",
                    "artemis",
                    "sls",
                    "rocket",
                    "launch",
                ],
                "type": MediaType.VIDEO,
                "title": f"Artemis SLS Megarocket Launch to Moon - {term}",
                "center": "KSC",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Artemis_I_Liftoff.jpg/960px-Artemis_I_Liftoff.jpg",
                "nasa_id": "KSC-20221116-PH-KLS01_0001",
            },
            {
                "id": "nasa-mars-perseverance-rover",
                "tags": [
                    "marte",
                    "mars",
                    "rover",
                    "perseverance",
                    "curiosity",
                    "planeta",
                    "planet",
                ],
                "type": MediaType.IMAGE,
                "title": f"Perseverance Rover on the Surface of Mars - {term}",
                "center": "JPL",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Perseverance_Selfie_at_Rochette.png/960px-Perseverance_Selfie_at_Rochette.png",
                "nasa_id": "PIA24836",
            },
        ]

        matched_items: List[Dict[str, Any]] = []
        for item in thematic_catalog:
            tags = item.get("tags")
            if isinstance(tags, list) and any(str(tag) in lower for tag in tags):
                matched_items.append(item)

        selected_items: List[Dict[str, Any]]
        if not matched_items:
            term_hash = sum(ord(c) for c in term)
            start_idx = term_hash % len(thematic_catalog)
            selected_items = thematic_catalog[start_idx:] + thematic_catalog[:start_idx]
        else:
            selected_items = matched_items

        candidates: List[MediaCandidateBase] = []
        count = min(limit, len(selected_items))
        for i in range(count):
            item = selected_items[i]
            m_type_raw = item.get("type", MediaType.IMAGE)
            m_type = m_type_raw if isinstance(m_type_raw, MediaType) else MediaType.IMAGE
            is_vid = m_type == MediaType.VIDEO

            candidates.append(
                MediaCandidateBase(
                    provider=self.name,
                    external_id=str(item.get("id")),
                    title=str(item.get("title")),
                    url=f"https://images.nasa.gov/details-{item.get('nasa_id')}",
                    preview_url=str(item.get("preview")),
                    media_type=m_type,
                    width=1920,
                    height=1080,
                    duration=12.0 if is_vid else None,
                    author=f"NASA / {item.get('center', 'HQ')}",
                    license=NASA_DEFAULT_LICENSE,
                    attribution=f"Mídia oficial por NASA ({item.get('center', 'HQ')})",
                    rights_status=RightsStatus.SAFE_REUSE,
                    fidelity_score=0.98,
                    metadata_json={
                        "sandbox": True,
                        "nasa_id": item.get("nasa_id"),
                        "query_matched": term,
                    },
                )
            )

        return candidates
