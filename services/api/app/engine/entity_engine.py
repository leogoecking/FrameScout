import logging
import re
from typing import List, Set, Tuple

from app.domain.enums import EntityCategory, QueryType
from app.domain.schemas import ExtractedEntity, SearchQueryBase

logger = logging.getLogger("framescout.engine.entity")

# 1. Dicionários e Bases de Conhecimento Especializadas

ORGANIZATION_KEYWORDS: Set[str] = {
    "take-two",
    "take two",
    "rockstar games",
    "rockstar",
    "crowdstrike",
    "microsoft",
    "nasa",
    "esa",
    "stsci",
    "space telescope science institute",
    "openai",
    "google",
    "apple",
    "meta",
    "amazon",
    "nvidia",
    "intel",
    "amd",
    "sony",
    "senado federal",
    "senado",
    "congresso",
    "governo",
    "stf",
    "fbi",
    "cia",
    "anatel",
    "smithsonian",
    "netflix",
    "disney",
    "warner",
}

PRODUCT_KEYWORDS: Set[str] = {
    "gta vi",
    "gta 6",
    "gta",
    "grand theft auto",
    "falcon sensor",
    "falcon",
    "windows 11",
    "windows 10",
    "windows",
    "linux",
    "macos",
    "ios",
    "android",
    "chatgpt",
    "gpt-4",
    "claude",
    "gemini",
    "james webb",
    "telescópio james webb",
    "hubble",
    "telescópio hubble",
    "artemis",
    "sls",
    "apollo 11",
    "apollo",
    "perseverance",
    "curiosity",
    "falcon 9",
    "starship",
    "voyager",
    "iss",
    "estação espacial",
    "iphone",
    "playstation",
    "xbox",
}

PERSON_KEYWORDS: Set[str] = {
    "sam altman",
    "satya nadella",
    "george lucas",
    "elon musk",
    "bill gates",
    "steve jobs",
    "jensen huang",
    "mark zuckerberg",
    "paula fernandes",
    "neil armstrong",
    "buzz aldrin",
    "alan turing",
}

TECHNOLOGY_KEYWORDS: Set[str] = {
    "inteligência artificial",
    "ia",
    "artificial intelligence",
    "ai",
    "machine learning",
    "deep learning",
    "redes neurais",
    "microchip",
    "semicondutor",
    "chip",
    "algoritmo",
    "código",
    "cibersegurança",
    "cybersecurity",
    "segurança digital",
    "kernel",
    "blue screen of death",
    "bsod",
    "tela azul",
    "computação em nuvem",
    "cloud computing",
    "nuvem",
    "banco de dados",
    "servidores",
    "datacenter",
    "satélite",
    "foguete",
    "astrofísica",
    "telescópio",
}

LOCATION_KEYWORDS: Set[str] = {
    "brasil",
    "estados unidos",
    "eua",
    "usa",
    "reino unido",
    "uk",
    "china",
    "japão",
    "alemanha",
    "frança",
    "rússia",
    "brasília",
    "são paulo",
    "rio de janeiro",
    "vale do silício",
    "silicon valley",
    "flórida",
    "cabo canaveral",
    "marte",
    "mars",
    "lua",
    "moon",
    "terra",
    "espaço",
    "space",
    "universo",
    "galáxia",
}

EVENT_KEYWORDS: Set[str] = {
    "apagão global",
    "apagão cibernético",
    "queda global",
    "vazamento",
    "vazamento de dados",
    "ataque hacker",
    "ciberataque",
    "invasão",
    "julgamento",
    "processo judicial",
    "audiência pública",
    "regulamentação",
    "pl 2.338",
    "pl 2338",
    "lançamento",
    "pouso na lua",
    "missão espacial",
    "conferência",
    "incidente",
}

# 2. Padrões Regex de Alta Precisão

DATE_PATTERNS = [
    r"\b\d{1,2}\s+de\s+(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)(?:\s+de\s+\d{4})?\b",
    r"\b(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+\d{4}\b",
    r"\b(?:em|no ano de|durante)\s+(?:19|20)\d{2}\b",
    r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b",
    r"\banos\s+(?:60|70|80|90|2000)\b",
]

PL_REGULATION_PATTERN = r"\b(?:PL|Projeto de Lei|Decreto|Emenda)\s+(?:n[º°]\s*)?[\d\.\-\/]+\b"


class EntityEngine:
    """
    Motor Heurístico de Reconhecimento e Extração de Entidades Nomeadas (NER).
    Mapeia termos do roteiro em 7 categorias principais:
    - ORGANIZATION, PRODUCT, PERSON, TECHNOLOGY, LOCATION, DATE_TIME, EVENT.
    """

    @classmethod
    def extract_entities(cls, text: str) -> List[ExtractedEntity]:
        """
        Extrai e categoriza entidades a partir de um texto ou narração.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        entities: List[ExtractedEntity] = []
        seen_spans: Set[Tuple[int, int]] = set()

        # 1. Regex de Datas e Períodos (DATE_TIME)
        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                span = match.span()
                if cls._span_overlaps(span, seen_spans):
                    continue
                matched_text = match.group(0).strip()
                seen_spans.add(span)
                entities.append(
                    ExtractedEntity(
                        text=matched_text,
                        category=EntityCategory.DATE_TIME,
                        confidence=0.95,
                        context=cls._extract_context(clean_text, span),
                    )
                )

        # 2. Regex de Projetos de Lei / Regulamentações (EVENT / ORGANIZATION)
        for match in re.finditer(PL_REGULATION_PATTERN, clean_text, re.IGNORECASE):
            span = match.span()
            if cls._span_overlaps(span, seen_spans):
                continue
            matched_text = match.group(0).strip()
            seen_spans.add(span)
            entities.append(
                ExtractedEntity(
                    text=matched_text,
                    category=EntityCategory.EVENT,
                    confidence=0.98,
                    context=cls._extract_context(clean_text, span),
                )
            )

        # 3. Mapeamento Direto por Dicionários Temáticos
        dict_categories = [
            (ORGANIZATION_KEYWORDS, EntityCategory.ORGANIZATION, 0.95),
            (PRODUCT_KEYWORDS, EntityCategory.PRODUCT, 0.95),
            (PERSON_KEYWORDS, EntityCategory.PERSON, 0.98),
            (EVENT_KEYWORDS, EntityCategory.EVENT, 0.90),
            (TECHNOLOGY_KEYWORDS, EntityCategory.TECHNOLOGY, 0.88),
            (LOCATION_KEYWORDS, EntityCategory.LOCATION, 0.85),
        ]

        for word_set, category, conf in dict_categories:
            # Ordenar por tamanho decrescente para priorizar expressões multi-palavra
            sorted_terms = sorted(word_set, key=len, reverse=True)
            for term in sorted_terms:
                pattern = r"\b" + re.escape(term) + r"\b"
                for match in re.finditer(pattern, clean_text, re.IGNORECASE):
                    span = match.span()
                    if cls._span_overlaps(span, seen_spans):
                        continue
                    matched_text = match.group(0).strip()
                    seen_spans.add(span)
                    entities.append(
                        ExtractedEntity(
                            text=matched_text,
                            category=category,
                            confidence=conf,
                            context=cls._extract_context(clean_text, span),
                        )
                    )

        # 4. Heurística de Nomes Próprios em Caixa Alta (Pessoas / Empresas Desconhecidas)
        proper_noun_pattern = r"\b[A-ZÀ-Ú][a-zà-ú]+(?:\s+[A-ZÀ-Ú][a-zà-ú]+){1,3}\b"
        for match in re.finditer(proper_noun_pattern, clean_text):
            span = match.span()
            if cls._span_overlaps(span, seen_spans):
                continue
            matched_text = match.group(0).strip()
            # Ignorar início de frases genéricas
            if matched_text.lower() in [
                "cena",
                "em julho",
                "o que",
                "por isso",
                "de acordo",
                "no entanto",
                "além disso",
            ]:
                continue
            seen_spans.add(span)
            entities.append(
                ExtractedEntity(
                    text=matched_text,
                    category=EntityCategory.ORGANIZATION
                    if any(
                        s in matched_text.lower()
                        for s in ["ltd", "inc", "corp", "studio", "labs", "tech"]
                    )
                    else EntityCategory.PERSON,
                    confidence=0.80,
                    context=cls._extract_context(clean_text, span),
                )
            )

        # 5. Ordenar por confiança decrescente e posição no texto
        entities.sort(key=lambda e: e.confidence, reverse=True)
        return entities

    @classmethod
    def generate_queries_from_entities(
        cls,
        entities: List[ExtractedEntity],
        scene_title: str = "",
    ) -> List[SearchQueryBase]:
        """
        Transforma a lista de entidades extraídas em um conjunto inteligente
        e diversificado de consultas de busca para os provedores de mídia.
        """
        if not entities:
            return []

        orgs = [e.text for e in entities if e.category == EntityCategory.ORGANIZATION]
        prods = [e.text for e in entities if e.category == EntityCategory.PRODUCT]
        people = [e.text for e in entities if e.category == EntityCategory.PERSON]
        techs = [e.text for e in entities if e.category == EntityCategory.TECHNOLOGY]
        events = [e.text for e in entities if e.category == EntityCategory.EVENT]
        locs = [e.text for e in entities if e.category == EntityCategory.LOCATION]

        queries: List[SearchQueryBase] = []
        seen_queries: Set[str] = set()

        def add_query(q_str: str, q_type: QueryType, priority: int) -> None:
            normalized = " ".join(q_str.split()).strip()
            if normalized and normalized.lower() not in seen_queries and len(normalized) > 3:
                seen_queries.add(normalized.lower())
                queries.append(
                    SearchQueryBase(
                        query=normalized,
                        query_type=q_type,
                        priority=priority,
                    )
                )

        # 1. Consultas Oficiais (Empresa + Produto)
        if orgs and prods:
            add_query(f"{orgs[0]} {prods[0]} official", QueryType.OFFICIAL, priority=1)
        elif orgs:
            add_query(f"{orgs[0]} official corporate logo", QueryType.OFFICIAL, priority=1)
        elif prods:
            add_query(f"{prods[0]} official", QueryType.OFFICIAL, priority=1)

        # 2. Consultas de Evento / Incidente (Entidade + Evento)
        if events:
            ev = events[0]
            if prods:
                add_query(f"{prods[0]} {ev}", QueryType.EVENT, priority=2)
            elif orgs:
                add_query(f"{orgs[0]} {ev}", QueryType.EVENT, priority=2)
            else:
                add_query(f"{ev} news report", QueryType.EVENT, priority=2)

        # 3. Consultas de Pessoas (Pessoa + Organização)
        if people:
            p = people[0]
            if orgs:
                add_query(f"{p} {orgs[0]}", QueryType.PERSON, priority=2)
            else:
                add_query(f"{p} portrait photo", QueryType.PERSON, priority=2)

        # 4. Consultas Técnicas / Conceituais
        if techs:
            t = techs[0]
            if prods:
                add_query(f"{prods[0]} {t} system", QueryType.CONCEPT, priority=3)
            elif locs:
                add_query(f"{t} in {locs[0]}", QueryType.CONCEPT, priority=3)
            else:
                add_query(f"{t} technology concept", QueryType.CONCEPT, priority=3)

        # 5. Consultas B-Roll cinemáticas
        if prods:
            add_query(f"{prods[0]} broll footage", QueryType.BROLL, priority=4)
        elif techs:
            add_query(f"{techs[0]} cinematic broll", QueryType.BROLL, priority=4)
        elif events:
            add_query(f"{events[0]} footage broll", QueryType.BROLL, priority=4)

        return queries

    @staticmethod
    def _span_overlaps(span: Tuple[int, int], spans: Set[Tuple[int, int]]) -> bool:
        start, end = span
        for s_start, s_end in spans:
            if max(start, s_start) < min(end, s_end):
                return True
        return False

    @staticmethod
    def _extract_context(text: str, span: Tuple[int, int], window: int = 40) -> str:
        start, end = span
        c_start = max(0, start - window)
        c_end = min(len(text), end + window)
        snippet = text[c_start:c_end].replace("\n", " ").strip()
        if c_start > 0:
            snippet = f"...{snippet}"
        if c_end < len(text):
            snippet = f"{snippet}..."
        return snippet
