import logging
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("framescout.engine.fidelity")

STOPWORDS: Set[str] = {
    "a",
    "o",
    "as",
    "os",
    "um",
    "uma",
    "uns",
    "umas",
    "de",
    "do",
    "da",
    "dos",
    "das",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "por",
    "pelo",
    "pela",
    "pelos",
    "pelas",
    "para",
    "com",
    "sem",
    "e",
    "ou",
    "que",
    "se",
    "mas",
    "como",
    "mais",
    "foi",
    "sao",
    "era",
    "eram",
    "ser",
    "estar",
    "ter",
    "ha",
    "the",
    "an",
    "of",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "and",
    "or",
    "to",
    "is",
    "are",
    "was",
    "were",
    "be",
    "this",
    "that",
    "it",
    "from",
    "apos",
    "cena",
    "exibindo",
}

KEY_DOMAIN_ENTITIES: Set[str] = {
    "crowdstrike",
    "windows",
    "microsoft",
    "falcon",
    "sensor",
    "gta",
    "vi",
    "take-two",
    "taketwo",
    "rockstar",
    "bsod",
    "outage",
    "leak",
    "hacker",
    "cyber",
    "server",
    "code",
    "airport",
    "flight",
    "terminal",
    "linux",
    "cloud",
    "intel",
    "amd",
    "nvidia",
    "apple",
    "google",
    "meta",
    "amazon",
    "youtube",
    "sony",
}


class FidelityEngine:
    """
    Motor de Ranqueamento Semântico e Cálculo do Fidelity Score (0 a 100).
    Avalia a aderência de cada mídia candidata ao roteiro e à intenção visual da cena.
    """

    @staticmethod
    def calculate_score(
        scene_narration: str,
        scene_visual_intent: Optional[str],
        scene_title: Optional[str],
        media_title: Optional[str] = None,
        media_provider: str = "pexels",
        media_width: Optional[int] = None,
        media_height: Optional[int] = None,
        media_type: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, Dict[str, float]]:
        """
        Calcula o Fidelity Score consolidado (0 a 100) e o detalhamento por dimensão.
        Fórmula:
        - 40% Similaridade Semântica
        - 25% Correspondência de Entidades
        - 15% Autoridade da Fonte
        - 10% Contexto Temporal / Histórico
        - 10% Qualidade Técnica
        """
        scene_context = f"{scene_title or ''} {scene_narration} {scene_visual_intent or ''}"
        media_context = (
            f"{media_title or ''} {FidelityEngine._extract_metadata_text(metadata_json)}"
        )

        # 1. Similaridade Semântica (40%)
        semantic_sim = FidelityEngine.compute_semantic_similarity(scene_context, media_context)

        # 2. Correspondência de Entidades (25%)
        entity_match = FidelityEngine.compute_entity_match(scene_context, media_context)

        # 3. Autoridade da Fonte (15%)
        source_auth = FidelityEngine.compute_source_authority(media_provider, metadata_json)

        # 4. Contexto Temporal (10%)
        temporal_match = FidelityEngine.compute_temporal_context(scene_context, media_context)

        # 5. Qualidade Técnica (10%)
        tech_quality = FidelityEngine.compute_technical_quality(media_width, media_height)

        raw_score = (
            (0.40 * semantic_sim)
            + (0.25 * entity_match)
            + (0.15 * source_auth)
            + (0.10 * temporal_match)
            + (0.10 * tech_quality)
        ) * 100.0

        final_score = max(0, min(100, int(round(raw_score))))

        breakdown = {
            "semantic": round(semantic_sim * 40.0, 1),
            "entities": round(entity_match * 25.0, 1),
            "authority": round(source_auth * 15.0, 1),
            "temporal": round(temporal_match * 10.0, 1),
            "quality": round(tech_quality * 10.0, 1),
            "total": float(final_score),
        }

        return final_score, breakdown

    @staticmethod
    def _extract_metadata_text(metadata_json: Optional[Dict[str, Any]]) -> str:
        if not metadata_json:
            return ""
        parts: List[str] = []
        for k in ["tags", "description", "categories", "author", "license_short_name"]:
            val = metadata_json.get(k)
            if isinstance(val, list):
                parts.extend(str(item) for item in val)
            elif isinstance(val, str):
                parts.append(val)
        return " ".join(parts)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [t.strip() for t in cleaned.split() if len(t.strip()) > 1]
        return [t for t in tokens if t not in STOPWORDS]

    @staticmethod
    def compute_semantic_similarity(text_a: str, text_b: str) -> float:
        """Calcula a similaridade baseada em termos e sobreposição."""
        tokens_a = FidelityEngine._tokenize(text_a)
        tokens_b = FidelityEngine._tokenize(text_b)

        if not tokens_a or not tokens_b:
            return 0.3

        set_a = set(tokens_a)
        set_b = set(tokens_b)

        common_words = set_a & set_b
        if not common_words:
            return 0.3

        # Contagem de palavras-chave compartilhadas com peso
        overlap_a = len(common_words) / len(set_a)
        overlap_b = len(common_words) / len(set_b)
        harmonic_overlap = (
            (2 * overlap_a * overlap_b) / (overlap_a + overlap_b)
            if (overlap_a + overlap_b) > 0
            else 0
        )

        # Term frequency dot product
        vec_a = {t: tokens_a.count(t) for t in set_a}
        vec_b = {t: tokens_b.count(t) for t in set_b}
        dot = sum(vec_a[w] * vec_b[w] for w in common_words)
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
        cosine = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0

        sim = max(cosine, harmonic_overlap, len(common_words) / min(len(set_a), 6))
        # Escalar para 0.35 (baixo) até 1.0 (muito alto)
        return min(1.0, max(0.2, 0.25 + (sim * 0.75)))

    @staticmethod
    def extract_entities(text: str) -> Set[str]:
        """Extrai entidades específicas, termos em caixa alta, siglas e termos-chave."""
        entities: Set[str] = set()
        acronyms = re.findall(r"\b[A-Z0-9]{2,}\b", text)
        entities.update(a.lower() for a in acronyms if a.lower() not in STOPWORDS)

        # CamelCase (ex: CrowdStrike, TakeTwo)
        camel = re.findall(r"\b[A-Z][a-z]+[A-Z][a-z]+\b", text)
        entities.update(c.lower() for c in camel)

        words = text.lower().split()
        for w in words:
            cleaned = re.sub(r"[^\w]", "", w)
            if cleaned in KEY_DOMAIN_ENTITIES:
                entities.add(cleaned)

        return entities

    @staticmethod
    def compute_entity_match(scene_text: str, media_text: str) -> float:
        """Pontua a correspondência exata de entidades cruciais."""
        scene_entities = FidelityEngine.extract_entities(scene_text)
        if not scene_entities:
            return 0.8  # Se a cena não tiver entidades estritas, não penaliza

        media_tokens = set(FidelityEngine._tokenize(media_text))
        media_raw_lower = media_text.lower()

        matched = 0
        for ent in scene_entities:
            if ent in media_tokens or ent in media_raw_lower:
                matched += 1

        if matched == 0:
            return 0.30

        match_ratio = matched / len(scene_entities)
        return min(1.0, 0.5 + (match_ratio * 0.5))

    @staticmethod
    def compute_source_authority(provider: str, metadata_json: Optional[Dict[str, Any]]) -> float:
        """Pontua a autoridade documental da fonte de procedência."""
        prov = provider.lower()
        if "nasa" in prov:
            return 0.98
        if "wikimedia" in prov:
            return 0.95
        if "openverse" in prov:
            return 0.90
        if "pexels" in prov:
            return 0.80
        if "official" in prov or (metadata_json and metadata_json.get("is_official")):
            return 1.00
        return 0.75

    @staticmethod
    def compute_temporal_context(scene_text: str, media_text: str) -> float:
        """Pontua a correspondência de contexto de ano/data entre a cena e a mídia."""
        scene_years = re.findall(r"\b(19\d{2}|20\d{2})\b", scene_text)
        if not scene_years:
            return 0.85

        media_years = re.findall(r"\b(19\d{2}|20\d{2})\b", media_text)
        if not media_years:
            return 0.60

        common_years = set(scene_years) & set(media_years)
        return 1.0 if common_years else 0.50

    @staticmethod
    def compute_technical_quality(width: Optional[int], height: Optional[int]) -> float:
        """Pontua a resolução técnica e adequação ao Full HD 1080p."""
        if not width or not height:
            return 0.75

        pixels = width * height
        if pixels >= 1920 * 1080:
            return 1.0
        if pixels >= 1280 * 720:
            return 0.85
        if pixels >= 800 * 600:
            return 0.70
        return 0.50
