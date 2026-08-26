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


class RenderStatus(str, enum.Enum):
    PENDING = "PENDING"
    SYNTHESIZING_AUDIO = "SYNTHESIZING_AUDIO"
    PROCESSING_MEDIA = "PROCESSING_MEDIA"
    RENDERING_VIDEO = "RENDERING_VIDEO"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AspectRatio(str, enum.Enum):
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"


class EntityCategory(str, enum.Enum):
    """
    Categorias de entidades nomeadas extraídas pelo EntityEngine (NER).
    """

    ORGANIZATION = "ORGANIZATION"
    PRODUCT = "PRODUCT"
    PERSON = "PERSON"
    TECHNOLOGY = "TECHNOLOGY"
    LOCATION = "LOCATION"
    DATE_TIME = "DATE_TIME"
    EVENT = "EVENT"


class ScriptTone(str, enum.Enum):
    DOCUMENTARY = "DOCUMENTARY"
    TECH_NEWS = "TECH_NEWS"
    EXPLAINER = "EXPLAINER"
    VIRAL_SHORTS = "VIRAL_SHORTS"
    DRAMATIC_STORYTELLING = "DRAMATIC_STORYTELLING"

