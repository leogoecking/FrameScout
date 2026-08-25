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

    async def search(self, query: SearchQueryBase, limit: int = 10) -> List[MediaCandidateBase]:
        # Se não houver chave de API configurada, utiliza o sandbox temático inteligente
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

    async def _search_remote(self, query: SearchQueryBase, limit: int) -> List[MediaCandidateBase]:
        headers = {"Authorization": self.api_key}
        candidates: List[MediaCandidateBase] = []
        half_limit = max(1, limit // 2)

        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Buscar Fotos
            try:
                photo_res = await client.get(
                    f"{self.base_url}/v1/search",
                    headers=headers,
                    params={"query": query.query, "per_page": half_limit},
                )
                if photo_res.status_code == 200:
                    photo_data = photo_res.json()
                    for p in photo_data.get("photos", []):
                        candidates.append(self._map_photo_to_candidate(p, query.query))
                else:
                    logger.warning(
                        f"Pexels Photos status {photo_res.status_code}: {photo_res.text[:100]}"
                    )
            except Exception as pe:
                logger.warning(f"Erro na requisição de fotos do Pexels: {pe}")

            # 2. Buscar Vídeos
            try:
                video_res = await client.get(
                    f"{self.base_url}/videos/search",
                    headers=headers,
                    params={"query": query.query, "per_page": half_limit},
                )
                if video_res.status_code == 200:
                    video_data = video_res.json()
                    for v in video_data.get("videos", []):
                        candidates.append(self._map_video_to_candidate(v, query.query))
                else:
                    logger.warning(
                        f"Pexels Videos status {video_res.status_code}: {video_res.text[:100]}"
                    )
            except Exception as ve:
                logger.warning(f"Erro na requisição de vídeos do Pexels: {ve}")

        # Se a busca remota não encontrou resultados, recorre ao sandbox
        if not candidates:
            return self._generate_sandbox_candidates(query, limit)

        return candidates[:limit]

    def _map_photo_to_candidate(self, photo: Dict[str, Any], query_term: str) -> MediaCandidateBase:
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

    def _map_video_to_candidate(self, video: Dict[str, Any], query_term: str) -> MediaCandidateBase:
        user_info = video.get("user", {})
        author = user_info.get("name", "Pexels Filmmaker")
        video_id = str(video.get("id"))

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
        Catálogo B-roll multi-temático e adaptativo que seleciona fotos e vídeos
        de acordo com as palavras-chave do projeto (Espaço, Games, Tecnologia,
        Natureza, Negócios, Culinária, História, Saúde, etc.).
        """
        term = query.query.strip()
        lower = term.lower()

        thematic_catalog = [
            # 1. Jogos & Games
            {
                "tags": [
                    "gta",
                    "game",
                    "jogo",
                    "games",
                    "gaming",
                    "console",
                    "gamer",
                    "rockstar",
                    "videogame",
                ],
                "type": MediaType.IMAGE,
                "title": f"Gamer Room & Neon Gaming Setup - {term}",
                "author": "Eren Li",
                "preview": "https://images.pexels.com/photos/7915574/pexels-photo-7915574.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "7915574",
            },
            {
                "tags": ["gta", "game", "jogo", "games", "gaming", "controller", "rockstar"],
                "type": MediaType.VIDEO,
                "title": f"Video Game Controller in Hands - {term}",
                "author": "Ron Lach",
                "preview": "https://images.pexels.com/photos/8111324/pexels-photo-8111324.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": 12.0,
                "id": "8111324",
            },
            # 2. Espaço & Universo
            {
                "tags": [
                    "espaco",
                    "espaço",
                    "space",
                    "astronauta",
                    "astronaut",
                    "universo",
                    "galaxia",
                    "estrela",
                ],
                "type": MediaType.IMAGE,
                "title": f"Galaxy, Stars & Cosmic Nebula - {term}",
                "author": "Felix Mittermeier",
                "preview": "https://images.pexels.com/photos/956999/milky-way-starry-sky-night-sky-star-956999.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "956999",
            },
            {
                "tags": ["espaco", "espaço", "space", "astronauta", "lua", "planeta"],
                "type": MediaType.IMAGE,
                "title": f"Full Moon and Night Sky - {term}",
                "author": "Pixabay",
                "preview": "https://images.pexels.com/photos/47367/full-moon-moon-bright-sky-47367.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "47367",
            },
            # 3. Negócios, Dinheiro & Finanças
            {
                "tags": [
                    "dinheiro",
                    "money",
                    "banco",
                    "bank",
                    "mercado",
                    "finance",
                    "empresa",
                    "economia",
                    "grafico",
                ],
                "type": MediaType.IMAGE,
                "title": f"Stock Market Charts & Financial Growth - {term}",
                "author": "Markus Spiske",
                "preview": "https://images.pexels.com/photos/187041/pexels-photo-187041.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "187041",
            },
            {
                "tags": [
                    "dinheiro",
                    "empresa",
                    "escritorio",
                    "escritório",
                    "business",
                    "office",
                    "meeting",
                ],
                "type": MediaType.VIDEO,
                "title": f"Business Team Meeting in Modern Office - {term}",
                "author": "fauxels",
                "preview": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": 10.0,
                "id": "3183150",
            },
            # 4. Comida & Gastronomia
            {
                "tags": [
                    "comida",
                    "food",
                    "cafe",
                    "café",
                    "coffee",
                    "restaurante",
                    "pizza",
                    "cozinha",
                    "chef",
                ],
                "type": MediaType.IMAGE,
                "title": f"Gourmet Coffee and Fresh Roast - {term}",
                "author": "Chevanon Photography",
                "preview": "https://images.pexels.com/photos/312418/pexels-photo-312418.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "312418",
            },
            {
                "tags": ["comida", "food", "restaurante", "cozinha", "pizza", "chef"],
                "type": MediaType.IMAGE,
                "title": f"Artisanal Culinary Dish Preparation - {term}",
                "author": "Trang Doan",
                "preview": "https://images.pexels.com/photos/1099680/pexels-photo-1099680.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "1099680",
            },
            # 5. Natureza & Paisagens
            {
                "tags": [
                    "natureza",
                    "nature",
                    "praia",
                    "beach",
                    "floresta",
                    "forest",
                    "montanha",
                    "mountain",
                    "mar",
                    "rio",
                ],
                "type": MediaType.IMAGE,
                "title": f"Breathtaking Mountain Landscape - {term}",
                "author": "eberhard grossgasteiger",
                "preview": "https://images.pexels.com/photos/443446/pexels-photo-443446.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "443446",
            },
            # 6. Cidade, Trânsito & Aeroportos
            {
                "tags": [
                    "cidade",
                    "city",
                    "aeroporto",
                    "airport",
                    "aviao",
                    "avião",
                    "voo",
                    "transito",
                    "rua",
                ],
                "type": MediaType.IMAGE,
                "title": f"Airport Terminal & Travel Journey - {term}",
                "author": "Anna Shvets",
                "preview": "https://images.pexels.com/photos/2026324/pexels-photo-2026324.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1280,
                "duration": None,
                "id": "2026324",
            },
            # 7. Saúde & Medicina
            {
                "tags": [
                    "medico",
                    "médico",
                    "hospital",
                    "saude",
                    "saúde",
                    "doctor",
                    "medicine",
                    "paciente",
                ],
                "type": MediaType.IMAGE,
                "title": f"Healthcare Professional at Work - {term}",
                "author": "Cedric Fauntleroy",
                "preview": "https://images.pexels.com/photos/4270088/pexels-photo-4270088.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "4270088",
            },
            # 8. História, Monumentos & Arquitetura
            {
                "tags": [
                    "historia",
                    "história",
                    "history",
                    "roma",
                    "rome",
                    "monumento",
                    "coliseu",
                    "colosseum",
                    "castelo",
                    "antigo",
                    "museu",
                    "arqueologia",
                ],
                "type": MediaType.IMAGE,
                "title": f"Historic Architecture and Ancient Heritage - {term}",
                "author": "Maurício Mascaro",
                "preview": "https://images.pexels.com/photos/71241/pexels-photo-71241.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "71241",
            },
            # 9. Direito, Justiça & Tribunais
            {
                "tags": [
                    "justica",
                    "justiça",
                    "tribunal",
                    "processo",
                    "advogado",
                    "lei",
                    "direito",
                    "court",
                    "law",
                    "judge",
                    "legal",
                ],
                "type": MediaType.IMAGE,
                "title": f"Legal Justice System and Law Books - {term}",
                "author": "Sora Shimazaki",
                "preview": "https://images.pexels.com/photos/5668772/pexels-photo-5668772.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "5668772",
            },
            # 8. Tecnologia, Código & Cibersegurança
            {
                "tags": [
                    "crowdstrike",
                    "bsod",
                    "windows",
                    "codigo",
                    "código",
                    "programacao",
                    "servidor",
                    "datacenter",
                    "cyber",
                    "software",
                    "tech",
                    "ti",
                ],
                "type": MediaType.IMAGE,
                "title": f"Datacenter Server Infrastructure - {term}",
                "author": "Manuel Geissinger",
                "preview": "https://images.pexels.com/photos/325229/pexels-photo-325229.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 1920,
                "height": 1080,
                "duration": None,
                "id": "325229",
            },
            {
                "tags": ["codigo", "código", "software", "terminal", "programador", "developer"],
                "type": MediaType.VIDEO,
                "title": f"Coding and Terminal Software Development - {term}",
                "author": "Pressmaster",
                "preview": "https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg?auto=compress&cs=tinysrgb&w=800",
                "width": 3840,
                "height": 2160,
                "duration": 14.5,
                "id": "3129957",
            },
        ]

        matched_items: List[Dict[str, Any]] = []
        for item in thematic_catalog:
            tags = item.get("tags")
            if isinstance(tags, list) and any(str(tag) in lower for tag in tags):
                matched_items.append(item)

        # Se não houver match direto, utiliza uma rotação baseada no hash do termo
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
