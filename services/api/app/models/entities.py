import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.enums import MediaType, RenderStatus, RightsStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="pt-BR", nullable=False)
    script_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    scenes: Mapped[List["Scene"]] = relationship(
        "Scene",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Scene.position",
    )
    render_jobs: Mapped[List["RenderJob"]] = relationship(
        "RenderJob",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="RenderJob.created_at.desc()",
    )


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    narration: Mapped[str] = mapped_column(Text, nullable=False)
    visual_intent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    end_estimate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="scenes")
    queries: Mapped[List["SearchQuery"]] = relationship(
        "SearchQuery",
        back_populates="scene",
        cascade="all, delete-orphan",
        order_by="SearchQuery.priority",
    )
    selected_assets: Mapped[List["SelectedAsset"]] = relationship(
        "SelectedAsset",
        back_populates="scene",
        cascade="all, delete-orphan",
        order_by="SelectedAsset.order_index",
    )


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(String(500), nullable=False)
    query_type: Mapped[str] = mapped_column(String(50), default="BROLL", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    scene: Mapped["Scene"] = relationship("Scene", back_populates="queries")
    media_candidates: Mapped[List["MediaCandidate"]] = relationship(
        "MediaCandidate", back_populates="search_query"
    )


class MediaCandidate(Base):
    __tablename__ = "media_candidates"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_query_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("search_queries.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    preview_url: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[MediaType] = mapped_column(
        SQLEnum(MediaType), default=MediaType.IMAGE, nullable=False
    )
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    license: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rights_status: Mapped[RightsStatus] = mapped_column(
        SQLEnum(RightsStatus), default=RightsStatus.REVIEW_REQUIRED, nullable=False
    )
    fidelity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    search_query: Mapped[Optional["SearchQuery"]] = relationship(
        "SearchQuery", back_populates="media_candidates"
    )
    selected_assets: Mapped[List["SelectedAsset"]] = relationship(
        "SelectedAsset", back_populates="media_candidate"
    )


class SelectedAsset(Base):
    __tablename__ = "selected_assets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False
    )
    media_candidate_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("media_candidates.id", ondelete="CASCADE"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    framing_mode: Mapped[str] = mapped_column(String(50), default="FILL", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    # Relationships
    scene: Mapped["Scene"] = relationship("Scene", back_populates="selected_assets")
    media_candidate: Mapped["MediaCandidate"] = relationship(
        "MediaCandidate", back_populates="selected_assets"
    )


class RenderJob(Base):
    __tablename__ = "render_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[RenderStatus] = mapped_column(
        SQLEnum(RenderStatus), default=RenderStatus.PENDING, nullable=False
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(10), default="16:9", nullable=False)
    voice: Mapped[str] = mapped_column(String(50), default="pt-BR-AntonioNeural", nullable=False)
    include_subtitles: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_credits_card: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="render_jobs")
