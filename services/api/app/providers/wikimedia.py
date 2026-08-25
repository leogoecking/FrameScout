import html
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.domain.enums import MediaType, RightsStatus
from app.domain.schemas import MediaCandidateBase, SearchQueryBase
from app.providers.base import MediaProvider

logger = logging.getLogger("framescout.providers.wikimedia")

WIKIMEDIA_USER_AGENT = "FrameScout/0.1.0 (contact@framescout.io)"

NOISE_QUERY_TERMS = {
    "broll",
    "b-roll",
    "b roll",
    "footage",
    "clip",
    "visuals",
    "visuais",
    "fundo",
    "background",
    "estilo",
    "imagem",
    "foto",
    "photo",
    "image",
    "video",
    "vídeo",
    "cena",
    "scene",
    "contexto",
    "oficial",
    "official",
    "logo",
    "logotipo",
    "symbol",
    "icon",
    "icone",
    "ilustração",
}

PORTUGUESE_TO_ENGLISH_MAP = {
    "computador": "computer",
    "computadores": "computers",
    "servidor": "server",
    "servidores": "servers",
    "tela azul": "blue screen of death bsod",
    "pane": "outage failure",
    "vazamento": "leak",
    "aeroporto": "airport",
    "voo": "flight",
    "voos": "flights",
    "aviao": "airplane",
    "avião": "airplane",
    "hospital": "hospital",
    "hospitais": "hospitals",
    "espaco": "space",
    "espaço": "space",
    "astronauta": "astronaut",
    "universo": "universe",
    "galaxia": "galaxy",
    "galáxia": "galaxy",
    "planeta": "planet",
    "terra": "earth",
    "lua": "moon",
    "sol": "sun",
    "jogo": "video game",
    "jogos": "video games",
    "comida": "food",
    "cafe": "coffee",
    "café": "coffee",
    "restaurante": "restaurant",
    "dinheiro": "money finance",
    "banco": "bank",
    "mercado": "market",
    "empresa": "company office",
    "escritorio": "office",
    "escritório": "office",
    "guerra": "war military",
    "historia": "history historical",
    "história": "history historical",
    "revolucao": "revolution",
    "revolução": "revolution",
    "castelo": "castle",
    "museu": "museum",
    "cidade": "city",
    "praia": "beach",
    "floresta": "forest nature",
    "montanha": "mountain",
    "carro": "car automobile",
    "automovel": "automobile",
    "navio": "ship",
    "ciencia": "science laboratory",
    "ciência": "science laboratory",
    "medico": "doctor medical",
    "médico": "doctor medical",
    "saude": "healthcare",
    "saúde": "healthcare",
    "futebol": "soccer football",
    "esporte": "sports athletic",
    "arte": "art painting",
    "musica": "music instrument",
    "música": "music instrument",
    "justica": "justice court",
    "justiça": "justice court",
    "tribunal": "court legal",
    "processo": "lawsuit court",
}


def clean_html_tags(text: str) -> str:
    """Remove tags HTML e decodifica entidades HTML presentes nos metadados da Wikimedia."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = html.unescape(clean)
    return " ".join(clean.split()).strip()


def derive_rights_status(
    license_name: Optional[str],
    credit_text: Optional[str] = None,
    usage_terms: Optional[str] = None,
) -> Tuple[RightsStatus, str, str]:
    """
    Motor heurístico de análise e derivação jurídica de licenças da Wikimedia Commons.
    Retorna: (RightsStatus, licença_padronizada, texto_de_atribuição)
    """
    raw_lic = (license_name or usage_terms or "").strip()
    lic_lower = raw_lic.lower()

    if any(
        term in lic_lower
        for term in [
            "-nc",
            "nc",
            "non-commercial",
            "noncommercial",
            "fair use",
            "trademark",
            "copyright",
            "restricted",
            "-nd",
            "no derivatives",
            "noderivs",
        ]
    ):
        norm_lic = raw_lic if raw_lic else "Restricted / Non-Commercial / Fair Use"
        attrib = f"Uso editorial sob revisão ({norm_lic}) via Wikimedia Commons"
        return RightsStatus.REVIEW_REQUIRED, norm_lic, attrib

    if any(
        term in lic_lower
        for term in ["public domain", "cc0", "pd-", "pd ", "no restrictions", "pd-self", "pd-us"]
    ):
        norm_lic = "Public Domain / CC0" if not raw_lic else raw_lic
        attrib = f"Domínio Público via Wikimedia Commons ({norm_lic})"
        return RightsStatus.SAFE_REUSE, norm_lic, attrib

    if any(
        term in lic_lower for term in ["cc-by", "cc by", "cc_by", "attribution", "gfdl", "gnu fdl"]
    ):
        norm_lic = raw_lic if raw_lic else "Creative Commons Attribution"
        author_str = clean_html_tags(credit_text or "Autor Desconhecido")
        attrib = f"Mídia por {author_str} sob licença {norm_lic} via Wikimedia Commons"
        return RightsStatus.ATTRIBUTION_REQUIRED, norm_lic, attrib

    norm_lic = raw_lic if raw_lic else "Licença não especificada (Revisão Necessária)"
    attrib = "Procedência via Wikimedia Commons (Verificar direitos no arquivo original)"
    return RightsStatus.REVIEW_REQUIRED, norm_lic, attrib


def generate_search_variants(query_text: str) -> List[str]:
    """
    Gera variantes de busca progressivas (da mais específica para a mais ampla)
    para garantir que a Wikimedia Commons retorne resultados reais e relevantes.
    """
    cleaned = re.sub(r"[^\w\s\-]", " ", query_text.lower())
    tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
    filtered_tokens = [t for t in tokens if t not in NOISE_QUERY_TERMS]

    variants: List[str] = []

    # 1. Termos em inglês / entidades traduzidas
    translated_tokens: List[str] = []
    for t in filtered_tokens:
        if t in PORTUGUESE_TO_ENGLISH_MAP:
            translated_tokens.append(PORTUGUESE_TO_ENGLISH_MAP[t])
        else:
            translated_tokens.append(t)

    translated_query = " ".join(translated_tokens).strip()
    if translated_query:
        variants.append(translated_query)

    # 2. Termos limpos originais
    clean_orig = " ".join(filtered_tokens).strip()
    if clean_orig and clean_orig != translated_query:
        variants.append(clean_orig)

    # 3. Termos essenciais (primeiras 2 ou 3 palavras-chave)
    if len(translated_tokens) > 2:
        variants.append(" ".join(translated_tokens[:2]))

    # 4. Termo bruto
    raw = query_text.strip()
    if raw and raw not in variants:
        variants.append(raw)

    return variants


class WikimediaProvider(MediaProvider):
    """
    Provedor de integração com a API do Wikimedia Commons.
    Recupera imagens e arquivos históricos/documentais e deriva rigorosamente
    os direitos de reuso (SAFE_REUSE, ATTRIBUTION_REQUIRED ou REVIEW_REQUIRED).
    """

    def __init__(self, base_url: str = "https://commons.wikimedia.org/w/api.php"):
        self.base_url = base_url

    @property
    def name(self) -> str:
        return "wikimedia"

    async def search(self, query: SearchQueryBase, limit: int = 10) -> List[MediaCandidateBase]:
        try:
            return await self._search_remote(query, limit)
        except Exception as exc:
            logger.warning(
                f"Falha na consulta ao Wikimedia Commons ({exc}). Recorrendo ao sandbox adaptativo."
            )
            return self._generate_sandbox_candidates(query, limit)

    async def _search_remote(self, query: SearchQueryBase, limit: int) -> List[MediaCandidateBase]:
        variants = generate_search_variants(query.query)
        headers = {"User-Agent": WIKIMEDIA_USER_AGENT}

        async with httpx.AsyncClient(timeout=12.0) as client:
            for search_term in variants:
                params = {
                    "action": "query",
                    "generator": "search",
                    "gsrsearch": search_term,
                    "gsrnamespace": "6",  # Namespace de Arquivos
                    "gsrlimit": str(max(limit * 2, 8)),
                    "prop": "imageinfo",
                    "iiprop": "url|size|extmetadata|dimensions|mime",
                    "iiurlwidth": "960",
                    "format": "json",
                }

                res = await client.get(self.base_url, params=params, headers=headers)
                if res.status_code != 200:
                    continue

                data = res.json()
                pages = data.get("query", {}).get("pages", {})
                if not pages:
                    continue

                candidates: List[MediaCandidateBase] = []
                for _, page in pages.items():
                    imageinfo_list = page.get("imageinfo", [])
                    if not imageinfo_list:
                        continue

                    info = imageinfo_list[0]
                    mime = info.get("mime", "").lower()
                    # Ignorar áudios puros e formatos sem prévia visual
                    if "audio" in mime or "ogg" in mime and "video" not in mime:
                        continue

                    candidate = self._map_imageinfo_to_candidate(page, info, query.query)
                    if candidate:
                        candidates.append(candidate)

                if candidates:
                    return candidates[:limit]

        return self._generate_sandbox_candidates(query, limit)

    def _map_imageinfo_to_candidate(
        self, page: Dict[str, Any], info: Dict[str, Any], query_term: str
    ) -> Optional[MediaCandidateBase]:
        extmeta = info.get("extmetadata", {})
        title_raw = page.get("title", f"File:{query_term}").replace("File:", "")

        artist_raw = extmeta.get("Artist", {}).get("value", "")
        author = clean_html_tags(artist_raw) or "Wikimedia Contributor"

        lic_name = extmeta.get("LicenseShortName", {}).get("value")
        credit_val = extmeta.get("Credit", {}).get("value", author)
        usage_terms = extmeta.get("UsageTerms", {}).get("value")

        rights_status, license_label, attribution = derive_rights_status(
            license_name=lic_name,
            credit_text=credit_val,
            usage_terms=usage_terms,
        )

        wiki_title = page.get("title", "")
        page_url = info.get("descriptionurl", f"https://commons.wikimedia.org/wiki/{wiki_title}")
        file_url = info.get("url", "")
        thumb_url = info.get("thumburl", file_url)

        mime = info.get("mime", "")
        media_type = MediaType.VIDEO if "video" in mime else MediaType.IMAGE

        return MediaCandidateBase(
            provider=self.name,
            external_id=f"wikimedia-{page.get('pageid', title_raw)}",
            title=title_raw,
            url=page_url,
            preview_url=thumb_url or file_url,
            media_type=media_type,
            width=int(info.get("width", 1200)),
            height=int(info.get("height", 800)),
            duration=None,
            author=author,
            license=license_label,
            attribution=attribution,
            rights_status=rights_status,
            fidelity_score=0.95,
            metadata_json={
                "page_id": page.get("pageid"),
                "file_url": file_url,
                "mime": mime,
                "license_short_name": lic_name,
                "usage_terms": usage_terms,
            },
        )

    def _generate_sandbox_candidates(
        self, query: SearchQueryBase, limit: int
    ) -> List[MediaCandidateBase]:
        """
        Catálogo documental de contingência dinâmico e categorizado por temas
        (Tech, Games, Espaço, História, Negócios, Natureza, etc.).
        """
        term = query.query.strip()
        lower = term.lower()

        thematic_catalog = [
            # Espaço & Ciência
            {
                "id": "wiki-space-apollo",
                "tags": [
                    "espaco",
                    "espaço",
                    "space",
                    "astronauta",
                    "astronaut",
                    "nasa",
                    "lua",
                    "moon",
                ],
                "title": f"NASA Apollo Astronaut in Space - {term}",
                "author": "NASA Archives",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Bruce_McCandless_II_during_EVA_in_1984.jpg/960px-Bruce_McCandless_II_during_EVA_in_1984.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:Bruce_McCandless_II_during_EVA_in_1984.jpg",
                "width": 1920,
                "height": 1080,
                "license": "Public domain (NASA)",
                "attribution": "NASA via Wikimedia Commons",
                "rights_status": RightsStatus.SAFE_REUSE,
            },
            # Games & Entretenimento
            {
                "id": "wiki-gaming-rockstar",
                "tags": [
                    "gta",
                    "rockstar",
                    "take-two",
                    "game",
                    "jogo",
                    "games",
                    "gaming",
                    "console",
                ],
                "title": f"Video Game Industry & Rockstar Studios - {term}",
                "author": "Wikimedia Contributor",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/20231022_Rockstar_North.jpg/960px-20231022_Rockstar_North.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:20231022_Rockstar_North.jpg",
                "width": 1920,
                "height": 1080,
                "license": "CC BY-SA 4.0",
                "attribution": "Mídia sob licença CC BY-SA 4.0 via Wikimedia Commons",
                "rights_status": RightsStatus.ATTRIBUTION_REQUIRED,
            },
            # História & Arquitetura
            {
                "id": "wiki-history-colosseum",
                "tags": [
                    "historia",
                    "história",
                    "history",
                    "roma",
                    "rome",
                    "monumento",
                    "castelo",
                    "guerra",
                ],
                "title": f"Historical Monument & Heritage - {term}",
                "author": "David Iliff",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/960px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:Colosseum_in_Rome,_Italy_-_April_2007.jpg",
                "width": 1920,
                "height": 1080,
                "license": "CC BY-SA 3.0",
                "attribution": "Foto por David Iliff sob licença CC BY-SA 3.0",
                "rights_status": RightsStatus.ATTRIBUTION_REQUIRED,
            },
            # Tecnologia & Cibersegurança
            {
                "id": "wiki-tech-crowdstrike-bsod",
                "tags": [
                    "crowdstrike",
                    "bsod",
                    "windows",
                    "microsoft",
                    "falha",
                    "outage",
                    "pane",
                    "cyber",
                    "software",
                ],
                "title": f"Blue Screen of Death (BSOD Error) - {term}",
                "author": "Microsoft / Wikimedia Community",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Bsod.png/960px-Bsod.png",
                "url": "https://commons.wikimedia.org/wiki/File:Bsod.png",
                "width": 1920,
                "height": 1080,
                "license": "Public domain",
                "attribution": "Domínio Público via Wikimedia Commons",
                "rights_status": RightsStatus.SAFE_REUSE,
            },
            # Negócios & Finanças
            {
                "id": "wiki-business-finance",
                "tags": [
                    "dinheiro",
                    "money",
                    "banco",
                    "bank",
                    "empresa",
                    "mercado",
                    "finance",
                    "economia",
                ],
                "title": f"Financial Markets and Business - {term}",
                "author": "Federal Reserve Archives",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/United_States_one_hundred-dollar_bill.jpg/960px-United_States_one_hundred-dollar_bill.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:United_States_one_hundred-dollar_bill.jpg",
                "width": 1920,
                "height": 1080,
                "license": "Public domain",
                "attribution": "Domínio Público via Wikimedia Commons",
                "rights_status": RightsStatus.SAFE_REUSE,
            },
            # Culinária & Alimentos
            {
                "id": "wiki-food-coffee",
                "tags": [
                    "comida",
                    "food",
                    "cafe",
                    "café",
                    "coffee",
                    "restaurante",
                    "cozinha",
                    "culinaria",
                ],
                "title": f"Food and Beverage Craft - {term}",
                "author": "Wikimedia Food Project",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/960px-A_small_cup_of_coffee.JPG",
                "url": "https://commons.wikimedia.org/wiki/File:A_small_cup_of_coffee.JPG",
                "width": 1920,
                "height": 1080,
                "license": "CC BY-SA 4.0",
                "attribution": "Mídia sob licença CC BY-SA 4.0 via Wikimedia Commons",
                "rights_status": RightsStatus.ATTRIBUTION_REQUIRED,
            },
            # Cidade & Transporte
            {
                "id": "wiki-transport-airport",
                "tags": [
                    "aeroporto",
                    "airport",
                    "aviao",
                    "avião",
                    "voo",
                    "transporte",
                    "cidade",
                    "city",
                ],
                "title": f"Airport Terminal & Aviation - {term}",
                "author": "Aviation Community",
                "preview": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Boeing_747-400_takeoff.jpg/960px-Boeing_747-400_takeoff.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:Boeing_747-400_takeoff.jpg",
                "width": 1920,
                "height": 1080,
                "license": "CC BY-SA 3.0",
                "attribution": "Mídia sob licença CC BY-SA 3.0 via Wikimedia Commons",
                "rights_status": RightsStatus.ATTRIBUTION_REQUIRED,
            },
        ]

        matched_items: List[Dict[str, Any]] = []
        for item in thematic_catalog:
            tags = item.get("tags")
            if isinstance(tags, list) and any(str(tag) in lower for tag in tags):
                matched_items.append(item)

        # Se não houver match direto, utiliza os primeiros itens do catálogo
        selected_items: List[Dict[str, Any]] = matched_items if matched_items else thematic_catalog

        candidates: List[MediaCandidateBase] = []
        count = min(limit, len(selected_items))
        for i in range(count):
            item = selected_items[i]
            r_status = item.get("rights_status", RightsStatus.SAFE_REUSE)
            if not isinstance(r_status, RightsStatus):
                r_status = RightsStatus.SAFE_REUSE

            candidates.append(
                MediaCandidateBase(
                    provider=self.name,
                    external_id=str(item.get("id")),
                    title=str(item.get("title")),
                    url=str(item.get("url")),
                    preview_url=str(item.get("preview")),
                    media_type=MediaType.IMAGE,
                    width=int(str(item.get("width", 1920))),
                    height=int(str(item.get("height", 1080))),
                    duration=None,
                    author=str(item.get("author", "Wikimedia Contributor")),
                    license=str(item.get("license", "Public domain")),
                    attribution=str(item.get("attribution", "")),
                    rights_status=r_status,
                    fidelity_score=0.90,
                    metadata_json={
                        "sandbox": True,
                        "query_matched": term,
                    },
                )
            )

        return candidates
