from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import MediaType, QueryType, RightsStatus


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
    scenes_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class SceneBase(BaseModel):
    position: int = Field(..., ge=1)
    title: Optional[str] = None
    narration: str
    visual_intent: Optional[str] = None
    start_estimate: Optional[float] = None
    end_estimate: Optional[float] = None


class SceneRead(SceneBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SearchQueryBase(BaseModel):
    query: str
    query_type: QueryType = QueryType.BROLL
    priority: int = 1


class SearchQueryRead(SearchQueryBase):
    id: UUID
    scene_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str
    version: str
    database: str
    timestamp: datetime
