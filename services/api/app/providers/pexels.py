import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import MediaCandidateBase, SearchQueryBase
from app.providers.base import MediaProvider

logger = logging.getLogger("framescout.providers.pexels")

PEXELS_LICENSE_LABEL = "Pexels License (Free for commercial use, no attribution required)"


class PexelsProvider(MediaProvider):
    """
    Provedor de integração com a API do Pexels (Fotos e Vídeos).
    Toda mídia do Pexels possui licença aberta de uso comercial,
    sendo classificada juridicamente como SAFE_REUSE.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else settings.PEXELS_API_KEY
        self.base_url = (base_url or "https://api.pexels.com").rstrip("/")

    @property
    def name(self) -> str:
        return "pexels"

    async def search(
        self, query: SearchQueryBase, limit: int = 10
    ) -> List[MediaCandidateBase]:
        # Se não houver chave de API configurada, utiliza o sandbox determinístico
        if not self.api_key or self.api_key.strip() in ["", "mock", "test"]:
            return self._generate_sandbox_candidates(query, limit)

        try:
            return await self._search_remote(query, limit)
        except Exception as exc:
            logger.warning(
                f"Falha na consulta remota ao Pexels ({exc}). "
                "Recorrendo ao sandbox de contingência."
            )
            return self._generate_sandbox_candidates(query, limit)

    async def _search_remote(
        self, query: SearchQueryBase, limit: int
    ) -> List[MediaCandidateBase]:
        headers = {"Authorization": self.api_key}
        candidates: List[MediaCandidateBase] = []
        half_limit = max(1, limit // 2)

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Buscar Fotos
            photo_res = await client.get(
                f"{self.base_url}/v1/search",
                headers=headers,
                params={"query": query.query, "per_page": half_limit},
            )
            if photo_res.status_code == 200:
                photo_data = photo_res.json()
                for p in photo_data.get("photos", []):
                    candidates.append(self._map_photo_to_candidate(p, query.query))

            # 2. Buscar Vídeos
            video_res = await client.get(
                f"{self.base_url}/videos/search",
                headers=headers,
                params={"query": query.query, "per_page": half_limit},
            )
            if video_res.status_code == 200:
                video_data = video_res.json()
                for v in video_data.get("videos", []):
                    candidates.append(self._map_video_to_candidate(v, query.query))

        return candidates[:limit]

    def _map_photo_to_candidate(
        self, photo: Dict[str, Any], query_term: str
    ) -> MediaCandidateBase:
        photographer = photo.get("photographer", "Pexels Creator")
        src = photo.get("src", {})
        photo_id = str(photo.get("id"))

        return MediaCandidateBase(
            provider=self.name,
            external_id=f"pexels-photo-{photo_id}",
            title=photo.get("alt") or f"Foto Pexels: {query_term}",
            url=photo.get("url", f"https://www.pexels.com/photo/{photo_id}/"),
            preview_url=src.get("medium") or src.get("large") or src.get("original", ""),
            media_type=MediaType.IMAGE,
            width=photo.get("width", 1920),
            height=photo.get("height", 1080),
            duration=None,
            author=photographer,
            license=PEXELS_LICENSE_LABEL,
            attribution=f"Foto por {photographer} no Pexels",
            rights_status=RightsStatus.SAFE_REUSE,
            fidelity_score=0.90,
            metadata_json={
                "pexels_id": photo_id,
                "photographer_url": photo.get("photographer_url"),
                "download_original": src.get("original"),
                "download_large2x": src.get("large2x"),
            },
        )

    def _map_video_to_candidate(
        self, video: Dict[str, Any], query_term: str
    ) -> MediaCandidateBase:
        user_info = video.get("user", {})
        author = user_info.get("name", "Pexels Filmmaker")
        video_id = str(video.get("id"))

        # Selecionar melhor arquivo de vídeo (HD ou original)
        files = video.get("video_files", [])
        best_file = next((f for f in files if f.get("quality") == "hd"), files[0] if files else {})
        download_url = best_file.get("link", "")

        return MediaCandidateBase(
            provider=self.name,
            external_id=f"pexels-video-{video_id}",
            title=f"Vídeo Pexels: {query_term}",
            url=video.get("url", f"https://www.pexels.com/video/{video_id}/"),
            preview_url=video.get("image") or download_url,
            media_type=MediaType.VIDEO,
            width=video.get("width", 1920),
            height=video.get("height", 1080),
            duration=float(video.get("duration", 10.0)),
            author=author,
            license=PEXELS_LICENSE_LABEL,
            attribution=f"Vídeo por {author} no Pexels",
            rights_status=RightsStatus.SAFE_REUSE,
            fidelity_score=0.92,
            metadata_json={
                "pexels_id": video_id,
                "author_url": user_info.get("url"),
                "download_link": download_url,
                "quality": best_file.get("quality", "hd"),
            },
        )

    def _generate_sandbox_candidates(
        self, query: SearchQueryBase, limit: int
    ) -> List[MediaCandidateBase]:
        """
        Gera candidatos realistas e seguros em modo sandbox offline
        para garantir execução determinística sem bloqueio por falta de chave de API.
        """
        term = query.query.strip()
        candidates: List[MediaCandidateBase] = []

        # Catálogo temático de imagens e vídeos de estoque Pexels/Unsplash CDN
        broll_catalog = [
            {
                "type": MediaType.IMAGE,
                "title": f"Servidores em Datacenter - {term}",
                "author": "Manuel Geissinger",
                "preview": "https://images.pexels.com/photos/325229/pexels-photo-325229.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "325229",
            },
            {
                "type": MediaType.VIDEO,
                "title": f"Linhas de Código e Terminal - {term}",
                "author": "Pressmaster",
                "preview": "https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 3840,
                "height": 2160,
                "duration": 14.5,
                "id": "3129957",
            },
            {
                "type": MediaType.IMAGE,
                "title": f"Saguão de Aeroporto e Painel de Voos - {term}",
                "author": "Anna Shvets",
                "preview": "https://images.pexels.com/photos/2026324/pexels-photo-2026324.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1280,
                "duration": None,
                "id": "2026324",
            },
            {
                "type": MediaType.VIDEO,
                "title": f"Monitor de Computador com Falha de Sistema - {term}",
                "author": "Mikhail Nilov",
                "preview": "https://images.pexels.com/photos/577585/pexels-photo-577585.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": 9.2,
                "id": "7534244",
            },
            {
                "type": MediaType.IMAGE,
                "title": f"Equipe de TI e Suporte Técnico - {term}",
                "author": "fauxels",
                "preview": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "3183150",
            },
            {
                "type": MediaType.IMAGE,
                "title": f"Mundo Digital e Cibersegurança - {term}",
                "author": "Kevin Ku",
                "preview": "https://images.pexels.com/photos/577585/pexels-photo-577585.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "577585",
            },
        ]

        count = min(limit, len(broll_catalog))
        for i in range(count):
            item = broll_catalog[i]
            dur_val = item["duration"]
            duration_float = float(str(dur_val)) if dur_val is not None else None

            candidates.append(
                MediaCandidateBase(
                    provider=self.name,
                    external_id=f"pexels-{item['id']}",
                    title=str(item["title"]),
                    url=f"https://www.pexels.com/photo/{item['id']}/",
                    preview_url=str(item["preview"]),
                    media_type=item["type"],  # type: ignore[arg-type]
                    width=int(str(item["width"])),
                    height=int(str(item["height"])),
                    duration=duration_float,
                    author=str(item["author"]),
                    license=PEXELS_LICENSE_LABEL,
                    attribution=f"Mídia por {item['author']} no Pexels",
                    rights_status=RightsStatus.SAFE_REUSE,
                    fidelity_score=0.90,
                    metadata_json={
                        "sandbox": True,
                        "pexels_id": item["id"],
                        "query_matched": term,
                    },
                )
            )

        return candidates
