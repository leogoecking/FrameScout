import enum


class RightsStatus(str, enum.Enum):
    """
    Classificação jurídica e de procedência para reutilização de mídia.
    A possibilidade técnica de baixar nunca implica direito de reutilização.
    """
    SAFE_REUSE = "SAFE_REUSE"  # Licença aberta verificada (CC0, Pexels, Domínio Público)
    ATTRIBUTION_REQUIRED = "ATTRIBUTION_REQUIRED"  # CC-BY, requer créditos claros
    REVIEW_REQUIRED = "REVIEW_REQUIRED"  # Termos ambíguos ou incompletos, alerta ao criador
    REFERENCE_ONLY = "REFERENCE_ONLY"  # Imprensa / material protegido, apenas referência visual
    BLOCKED = "BLOCKED"  # Proibido / copyright restritivo / não selecionável


class MediaType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class QueryType(str, enum.Enum):
    OFFICIAL = "OFFICIAL"
    EVENT = "EVENT"
    COMPANY = "COMPANY"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    CONCEPT = "CONCEPT"
    BROLL = "BROLL"
