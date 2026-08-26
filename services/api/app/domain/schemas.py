from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.enums import (
    EntityCategory,
    MediaType,
    QueryType,
    RenderStatus,
    RightsStatus,
    ScriptTone,
)

# --- Project Schemas ---


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    language: str = Field(default="pt-BR", max_length=10)
    script_raw: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    language: Optional[str] = Field(None, max_length=10)
    script_raw: Optional[str] = None


class ProjectRead(ProjectBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    scenes_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# --- Search Query Schemas ---


class SearchQueryBase(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    query_type: QueryType = QueryType.BROLL
    priority: int = Field(default=1, ge=1, le=5)

    @field_validator("query_type", mode="before")
    @classmethod
    def normalize_query_type(cls, v: Any) -> QueryType:
        if isinstance(v, str):
            try:
                return QueryType(v.upper())
            except ValueError:
                return QueryType.BROLL
        if isinstance(v, QueryType):
            return v
        return QueryType.BROLL


class SearchQueryCreate(SearchQueryBase):
    pass


class SearchQueryUpdate(BaseModel):
    query: Optional[str] = Field(None, min_length=1, max_length=500)
    query_type: Optional[QueryType] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

    @field_validator("query_type", mode="before")
    @classmethod
    def normalize_query_type(cls, v: Any) -> Optional[QueryType]:
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return QueryType(v.upper())
            except ValueError:
                return QueryType.BROLL
        if isinstance(v, QueryType):
            return v
        return None


class SearchQueryRead(SearchQueryBase):
    id: UUID
    scene_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Media Candidate Schemas ---


class MediaCandidateBase(BaseModel):
    provider: str
    external_id: str
    title: Optional[str] = None
    url: str
    preview_url: str
    media_type: MediaType = MediaType.IMAGE
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    author: Optional[str] = None
    license: Optional[str] = None
    attribution: Optional[str] = None
    rights_status: RightsStatus = RightsStatus.REVIEW_REQUIRED
    fidelity_score: Optional[float] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class MediaCandidateRead(MediaCandidateBase):
    id: UUID
    search_query_id: Optional[UUID] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Selected Asset Schemas ---


class SelectedAssetBase(BaseModel):
    order_index: int = Field(default=0, ge=0)
    framing_mode: str = Field(default="FILL", max_length=50)
    notes: Optional[str] = None


class SelectedAssetCreate(BaseModel):
    media_candidate_id: UUID
    order_index: Optional[int] = 0
    framing_mode: Optional[str] = "FILL"
    notes: Optional[str] = None


class SelectedAssetUpdate(BaseModel):
    order_index: Optional[int] = None
    framing_mode: Optional[str] = None
    notes: Optional[str] = None


class SelectedAssetRead(SelectedAssetBase):
    id: UUID
    scene_id: UUID
    media_candidate_id: UUID
    created_at: datetime
    media_candidate: Optional[MediaCandidateRead] = None

    model_config = ConfigDict(from_attributes=True)


# --- Scene Schemas ---


class SceneBase(BaseModel):
    position: int = Field(..., ge=1)
    title: Optional[str] = Field(None, max_length=255)
    narration: str
    visual_intent: Optional[str] = None
    start_estimate: Optional[float] = None
    end_estimate: Optional[float] = None


class SceneCreate(BaseModel):
    position: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=255)
    narration: str
    visual_intent: Optional[str] = None
    start_estimate: Optional[float] = None
    end_estimate: Optional[float] = None


class SceneUpdate(BaseModel):
    position: Optional[int] = Field(None, ge=1)
    title: Optional[str] = Field(None, max_length=255)
    narration: Optional[str] = None
    visual_intent: Optional[str] = None
    start_estimate: Optional[float] = None
    end_estimate: Optional[float] = None


class SceneRead(SceneBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime
    queries: List[SearchQueryRead] = Field(default_factory=list)
    selected_assets: List[SelectedAssetRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SceneReorderRequest(BaseModel):
    scene_ids: List[UUID]


class SceneSplitRequest(BaseModel):
    first_part_narration: str
    second_part_narration: str
    first_part_title: Optional[str] = None
    second_part_title: Optional[str] = None
    first_part_visual_intent: Optional[str] = None
    second_part_visual_intent: Optional[str] = None


class SceneMergeRequest(BaseModel):
    target_scene_id: UUID


# --- Visual Plan Export Schemas ---


class SceneVisualPlanItem(BaseModel):
    scene_position: int
    scene_title: str
    narration: str
    visual_intent: Optional[str] = None
    start_estimate: float
    end_estimate: float
    duration: float
    selected_asset: Optional[SelectedAssetRead] = None


class VisualPlanExport(BaseModel):
    project_id: UUID
    project_name: str
    language: str
    total_scenes: int
    covered_scenes_count: int
    total_duration_seconds: float
    scenes: List[SceneVisualPlanItem]
    consolidated_attributions: List[str]
    markdown_document: str


# --- Render Job Schemas ---


class RenderJobCreate(BaseModel):
    aspect_ratio: Optional[str] = "16:9"
    voice: Optional[str] = "pt-BR-AntonioNeural"
    include_subtitles: Optional[bool] = True
    include_credits_card: Optional[bool] = True


class RenderJobRead(BaseModel):
    id: UUID
    project_id: UUID
    status: RenderStatus
    progress: int
    aspect_ratio: str
    voice: str
    include_subtitles: bool
    include_credits_card: bool
    video_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Entity Extraction Schemas (Sprint 13) ---


class ExtractedEntity(BaseModel):
    text: str = Field(..., description="Texto da entidade extraída")
    category: EntityCategory = Field(..., description="Categoria classificada da entidade")
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0, description="Confiança heurística da detecção"
    )
    context: Optional[str] = Field(None, description="Trecho de contexto onde foi detectada")


class SceneEntitiesResponse(BaseModel):
    scene_id: UUID
    scene_position: int
    entities: List[ExtractedEntity]
    suggested_queries: List[SearchQueryBase]


class ProjectEntitiesResponse(BaseModel):
    project_id: UUID
    total_entities_count: int
    entities_by_category: Dict[str, List[str]]
    scenes_entities: List[SceneEntitiesResponse]


# --- AI Generation Schemas ---


class AIGenerateImageRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Prompt customizado ou refinado pelo usuário")
    aspect_ratio: Optional[str] = Field(
        "16:9", description="Proporção da imagem: '16:9', '9:16' ou '1:1'"
    )
    count: Optional[int] = Field(
        2, ge=1, le=4, description="Quantidade de variações a gerar (1 a 4)"
    )


class GenerateScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="Tema ou assunto principal do vídeo")
    tone: Optional[ScriptTone] = Field(
        default=ScriptTone.DOCUMENTARY, description="Tom e estilo narrativo"
    )
    target_duration: Optional[str] = Field(
        default="3m", description="Duração estimada: '60s', '3m', '5m' ou '10m'"
    )
    target_language: Optional[str] = Field(default="pt-BR", description="Idioma do roteiro")
    context_notes: Optional[str] = Field(
        default=None, description="Pontos-chave ou instruções adicionais"
    )
    auto_generate_scenes: Optional[bool] = Field(
        default=False, description="Se True, divide o roteiro gerado em cenas imediatamente"
    )


class GenerateScriptResponse(BaseModel):
    title: str
    topic: str
    tone: ScriptTone
    estimated_duration_seconds: int
    word_count: int
    script_raw: str
    hook: Optional[str] = None
    call_to_action: Optional[str] = None


# --- Health Schemas ---


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str
    database: str
    timestamp: datetime
