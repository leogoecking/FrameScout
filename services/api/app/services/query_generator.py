import re
from typing import List, Optional, Set

from app.domain.enums import QueryType
from app.domain.schemas import SearchQueryCreate
from app.engine.entity_engine import EntityEngine

# Stop words in Portuguese and English to filter out noisy terms in query construction
STOP_WORDS = {
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
    "sobre",
    "entre",
    "que",
    "se",
    "e",
    "ou",
    "mas",
    "como",
    "mais",
    "foi",
    "foram",
    "era",
    "eram",
    "sao",
    "são",
    "ser",
    "ter",
    "está",
    "estao",
    "estão",
    "apenas",
    "quando",
    "depois",
    "hoje",
    "entao",
    "então",
    "aqui",
    "ali",
    "onde",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "with",
    "by",
    "from",
    "of",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
}

# Known entity and brand aliases map
KNOWN_COMPANIES = {
    "take-two": "Take-Two Interactive",
    "take two": "Take-Two Interactive",
    "rockstar": "Rockstar Games",
    "crowdstrike": "CrowdStrike",
    "microsoft": "Microsoft",
    "windows": "Microsoft Windows",
    "apple": "Apple",
    "google": "Google",
    "openai": "OpenAI",
    "sony": "Sony",
    "nintendo": "Nintendo",
    "valve": "Valve",
    "meta": "Meta",
    "amazon": "Amazon",
    "nvidia": "NVIDIA",
    "embraer": "Embraer",
    "petrobras": "Petrobras",
    "vale": "Vale",
}

KNOWN_PRODUCTS_OR_EVENTS = {
    "gta vi": "GTA VI",
    "gta 6": "GTA 6",
    "grand theft auto": "Grand Theft Auto",
    "falcon sensor": "CrowdStrike Falcon",
    "bsod": "Blue Screen of Death BSOD",
    "tela azul": "Blue Screen of Death",
}


def clean_query_term(text: str) -> str:
    """Remove pontuações desnecessárias e múltiplos espaços."""
    cleaned = re.sub(r"[^\w\s\-\.]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_keywords(text: str, max_words: int = 6) -> List[str]:
    """Extrai palavras-chave relevantes descartando stop words."""
    words = re.findall(r"\b[a-zA-ZÀ-ÿ0-9\-\.\_]+\b", text)
    filtered = [w for w in words if w.lower() not in STOP_WORDS and len(w) > 1]
    return filtered[:max_words]


def detect_companies(text: str) -> Set[str]:
    lower = text.lower()
    found = set()
    for key, official_name in KNOWN_COMPANIES.items():
        if re.search(rf"\b{re.escape(key)}\b", lower):
            found.add(official_name)
    return found


def detect_products(text: str) -> Set[str]:
    lower = text.lower()
    found = set()
    for key, official_name in KNOWN_PRODUCTS_OR_EVENTS.items():
        if re.search(rf"\b{re.escape(key)}\b", lower):
            found.add(official_name)
    return found


class QueryGenerator:
    """
    Motor determinístico de geração de consultas de busca categorizadas
    por intenção (Fidelidade/Evento, Fonte Oficial, B-Roll, Conceito).
    """

    @classmethod
    def generate(
        cls,
        narration: str,
        visual_intent: Optional[str] = None,
        title: Optional[str] = None,
    ) -> List[SearchQueryCreate]:
        if not narration or not narration.strip():
            return []

        full_text = f"{title or ''} {narration} {visual_intent or ''}".strip()
        queries: List[SearchQueryCreate] = []
        seen_queries: Set[str] = set()

        companies = detect_companies(full_text)
        products = detect_products(full_text)

        # Extrair entidades com letras maiúsculas suportando acentuação
        proper_nouns = re.findall(
            r"\b[A-ZÀ-ÖØ-Þ][a-zA-ZÀ-ÿ0-9]*(?:[-][A-ZÀ-ÖØ-Þ][a-zA-ZÀ-ÿ0-9]*)*(?:\s+[A-ZÀ-ÖØ-Þ][a-zA-ZÀ-ÿ0-9]*)*\b",
            narration,
        )
        proper_nouns = [
            p.strip() for p in proper_nouns if p.lower() not in STOP_WORDS and len(p.strip()) > 2
        ]

        keywords = extract_keywords(narration, max_words=6)

        # -------------------------------------------------------------
        # 1. EVENT / FIDELITY QUERY (Prioridade 1 - Fato Histórico/Evento)
        # -------------------------------------------------------------
        event_parts: List[str] = []
        if products:
            event_parts.extend(list(products)[:2])
        if companies:
            event_parts.extend(list(companies)[:2])

        if not event_parts and proper_nouns:
            event_parts.extend(proper_nouns[:2])

        # Adicionar termos de ação/evento relevantes
        lower = full_text.lower()
        if "vazamento" in lower or "leak" in lower:
            event_parts.append("leak investigation")
        elif "pane" in lower or "outage" in lower or "interrupção" in lower:
            event_parts.append("global outage")
        elif "aeroporto" in lower or "voos" in lower:
            event_parts.append("airport flight cancelation")
        elif "hospital" in lower:
            event_parts.append("hospital computer systems failure")
        elif "processo" in lower or "court" in lower or "legal" in lower:
            event_parts.append("court legal action")

        if not event_parts:
            event_parts = keywords[:4]

        event_query_str = clean_query_term(" ".join(event_parts))
        if (
            event_query_str
            and len(event_query_str) > 2
            and event_query_str.lower() not in seen_queries
        ):
            seen_queries.add(event_query_str.lower())
            queries.append(
                SearchQueryCreate(
                    query=event_query_str,
                    query_type=QueryType.EVENT,
                    priority=1,
                )
            )

        # -------------------------------------------------------------
        # 2. OFFICIAL / COMPANY QUERY (Prioridade 2 - Fontes Oficiais)
        # -------------------------------------------------------------
        for comp in list(companies)[:2]:
            official_q = clean_query_term(f"{comp} official logo")
            if official_q.lower() not in seen_queries:
                seen_queries.add(official_q.lower())
                queries.append(
                    SearchQueryCreate(
                        query=official_q,
                        query_type=QueryType.OFFICIAL,
                        priority=2,
                    )
                )

        if not companies and proper_nouns:
            first_proper = proper_nouns[0]
            # Validar que a entidade própria tem substância
            if len(first_proper.split()) > 0 and first_proper.lower() not in STOP_WORDS:
                official_q = clean_query_term(f"{first_proper} official")
                if official_q.lower() not in seen_queries:
                    seen_queries.add(official_q.lower())
                    queries.append(
                        SearchQueryCreate(
                            query=official_q,
                            query_type=QueryType.COMPANY,
                            priority=2,
                        )
                    )

        # -------------------------------------------------------------
        # 3. B-ROLL QUERY (Prioridade 3 - Mídia Atmosférica de Apoio)
        # -------------------------------------------------------------
        broll_terms: List[str] = []
        if visual_intent and visual_intent.strip():
            v_clean = re.sub(
                r"^(?:B-roll de|Material visual representativo:?|Imagens de|B-roll)\s*",
                "",
                visual_intent,
                flags=re.IGNORECASE,
            ).strip()
            if v_clean and len(v_clean) > 2:
                broll_terms.append(clean_query_term(f"{v_clean} broll"))

        if not broll_terms:
            if any(k in lower for k in ["tela azul", "bsod", "erro"]):
                broll_terms.append("blue screen of death computer error broll")
            elif any(k in lower for k in ["aeroporto", "voo", "saguão"]):
                broll_terms.append("crowded airport terminal departure board broll")
            elif any(k in lower for k in ["servidor", "datacenter", "computador"]):
                broll_terms.append("data center servers flashing lights broll")
            elif any(k in lower for k in ["game", "jogo", "gta", "vazamento", "leak"]):
                broll_terms.append("gaming development code investigation broll")
            elif keywords:
                broll_terms.append(clean_query_term(f"{' '.join(keywords[:3])} broll"))

        for b_q in broll_terms:
            if b_q and b_q.lower() != "broll" and b_q.lower() not in seen_queries:
                seen_queries.add(b_q.lower())
                queries.append(
                    SearchQueryCreate(
                        query=b_q,
                        query_type=QueryType.BROLL,
                        priority=3,
                    )
                )

        # -------------------------------------------------------------
        # 4. CONCEPT QUERY (Prioridade 3 - Conceito/Metáfora)
        # -------------------------------------------------------------
        concept_terms: List[str] = []
        if any(k in lower for k in ["vazamento", "leak", "processo", "identificar"]):
            concept_terms.append("intellectual property leak legal investigation")
        elif any(k in lower for k in ["atualização", "software", "falha", "bug"]):
            concept_terms.append("software update failure cybersecurity crash")
        elif any(k in lower for k in ["aeroporto", "caos", "passageiros"]):
            concept_terms.append("global travel disruption passenger delay")

        for c_q in concept_terms:
            if c_q and c_q.lower() not in seen_queries:
                seen_queries.add(c_q.lower())
                queries.append(
                    SearchQueryCreate(
                        query=c_q,
                        query_type=QueryType.CONCEPT,
                        priority=3,
                    )
                )

        # -------------------------------------------------------------
        # 5. ENTITY-DERIVED QUERIES (Sprint 13 - Enriquecimento por NER)
        # -------------------------------------------------------------
        try:
            extracted_entities = EntityEngine.extract_entities(full_text)
            entity_queries = EntityEngine.generate_queries_from_entities(
                extracted_entities, title or ""
            )
            for eq in entity_queries:
                if eq.query.lower() not in seen_queries:
                    seen_queries.add(eq.query.lower())
                    queries.append(
                        SearchQueryCreate(
                            query=eq.query,
                            query_type=eq.query_type,
                            priority=eq.priority,
                        )
                    )
        except Exception:
            pass

        # Garantir pelo menos uma query de B-roll se o conjunto estiver vazio ou pequeno
        if not queries and title:
            queries.append(
                SearchQueryCreate(
                    query=clean_query_term(f"{title} broll"),
                    query_type=QueryType.BROLL,
                    priority=2,
                )
            )

        return queries
