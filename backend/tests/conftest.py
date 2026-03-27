import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.persistence.db import get_db

from app.persistence.base import Base
from app.persistence.tables import VideoJob, VideoAsset, SnapshotConfig


load_dotenv()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()

@pytest.fixture
def job(db_session):
    job = VideoJob(job_id="job-123", status="created")
    db_session.add(job)
    db_session.flush()
    return job


@pytest.fixture
def video_asset(db_session, job, tmp_path):
    video_path = tmp_path / "video.mp4"
    video_path.touch()

    asset = VideoAsset(
        job_id=job.job_id,
        uri=str(video_path),
    )
    db_session.add(asset)
    db_session.flush()
    return asset


@pytest.fixture
def snapshot_config(db_session, job):
    cfg = SnapshotConfig(
        job_id=job.job_id,
        sampling_fps=2.0,
        chunk_length_sec=10,
        resize_width=256,
        grayscale=False,
        black_white=False,
        image_format="jpg",
    )
    db_session.add(cfg)
    db_session.flush()
    return cfg

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()