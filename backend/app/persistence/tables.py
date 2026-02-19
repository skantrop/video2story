import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean,
    Text,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.persistence.base import Base


class VideoJob(Base):
    __tablename__ = "video_job"

    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    status = Column(String, nullable=False, default="created")
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    # 1:1
    asset = relationship(
        "VideoAsset",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )

    snapshot_config = relationship(
        "SnapshotConfig",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )

    narrative = relationship(
        "Narrative",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # 1:many
    snapshots = relationship(
        "Snapshot",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    scenes = relationship(
        "Scene",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class VideoAsset(Base):
    __tablename__ = "video_asset"

    video_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String,
        ForeignKey("video_job.job_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    uri = Column(String, nullable=False)

    job = relationship("VideoJob", back_populates="asset")


class SnapshotConfig(Base):
    __tablename__ = "snapshot_config"

    config_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String,
        ForeignKey("video_job.job_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    sampling_fps = Column(Float, nullable=False, default=1.0)
    chunk_length_sec = Column(Integer, nullable=False, default=10)
    resize_width = Column(Integer, nullable=True)
    grayscale = Column(Boolean, nullable=False, default=False)
    black_white = Column(Boolean, nullable=False, default=False)
    image_format = Column(String, nullable=False, default="jpg")

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    job = relationship("VideoJob", back_populates="snapshot_config", uselist=False)


class Snapshot(Base):
    __tablename__ = "snapshot"

    snapshot_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String,
        ForeignKey("video_job.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    timestamp_sec = Column(Float, nullable=False)
    uri = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    job = relationship("VideoJob", back_populates="snapshots")

    scene_links = relationship(
        "SceneSnapshot",
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("job_id", "timestamp_sec", name="uq_snapshot_job_timestamp"),
        Index("ix_snapshot_job_time", "job_id", "timestamp_sec"),
    )


class Scene(Base):
    __tablename__ = "scene"

    scene_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String,
        ForeignKey("video_job.job_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_sec = Column(Float, nullable=False)
    end_sec = Column(Float, nullable=False)

    short_description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    job = relationship("VideoJob", back_populates="scenes")

    snapshot_links = relationship(
        "SceneSnapshot",
        back_populates="scene",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_scene_job_start", "job_id", "start_sec"),
    )


class SceneSnapshot(Base):
    __tablename__ = "scene_snapshot"

    scene_id = Column(
        String,
        ForeignKey("scene.scene_id", ondelete="CASCADE"),
        primary_key=True,
    )
    snapshot_id = Column(
        String,
        ForeignKey("snapshot.snapshot_id", ondelete="CASCADE"),
        primary_key=True,
    )

    evidence = Column(Text, nullable=True)
    score = Column(Float, nullable=True)

    scene = relationship("Scene", back_populates="snapshot_links")
    snapshot = relationship("Snapshot", back_populates="scene_links")


class Narrative(Base):
    __tablename__ = "narrative"

    narrative_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(
        String,
        ForeignKey("video_job.job_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    short_summary = Column(Text, nullable=False)
    full_story = Column(Text, nullable=False)

    structured_data = Column(JSONB, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=text("now()"))

    job = relationship("VideoJob", back_populates="narrative", uselist=False)