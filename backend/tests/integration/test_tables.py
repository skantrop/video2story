import pytest
from sqlalchemy.exc import IntegrityError

from app.persistence.tables import (
    VideoJob,
    VideoAsset,
    SnapshotConfig,
    Snapshot,
    Scene,
    SceneSnapshot,
    Narrative,
)


def test_video_job_relationships(db_session):
    job = VideoJob(job_id="job1", status="created")

    asset = VideoAsset(
        job_id=job.job_id,
        uri="/tmp/video.mp4",
    )

    cfg = SnapshotConfig(
        job_id=job.job_id,
        sampling_fps=1.0,
        chunk_length_sec=10,
        resize_width=256,
        grayscale=False,
        black_white=False,
        image_format="jpg",
    )

    db_session.add_all([job, asset, cfg])
    db_session.commit()

    saved = db_session.query(VideoJob).filter_by(job_id="job1").one()

    assert saved.asset is not None
    assert saved.asset.uri == "/tmp/video.mp4"

    assert saved.snapshot_config is not None
    assert saved.snapshot_config.sampling_fps == 1.0


def test_snapshot_unique_constraint(db_session):
    job = VideoJob(job_id="job2", status="created")
    db_session.add(job)
    db_session.flush()

    s1 = Snapshot(
        job_id=job.job_id,
        timestamp_sec=1.0,
        uri="/tmp/1.jpg",
        width=100,
        height=50,
    )

    s2 = Snapshot(
        job_id=job.job_id,
        timestamp_sec=1.0,
        uri="/tmp/2.jpg",
        width=100,
        height=50,
    )

    db_session.add_all([s1, s2])

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_scene_snapshot_link(db_session):
    job = VideoJob(job_id="job3", status="created")
    db_session.add(job)
    db_session.flush()

    snapshot = Snapshot(
        job_id=job.job_id,
        timestamp_sec=0.0,
        uri="/tmp/frame.jpg",
        width=100,
        height=50,
    )

    scene = Scene(
        job_id=job.job_id,
        start_sec=0.0,
        end_sec=5.0,
        short_description="Someone walks in",
        confidence=0.9,
    )

    db_session.add_all([snapshot, scene])
    db_session.flush()

    link = SceneSnapshot(
        scene_id=scene.scene_id,
        snapshot_id=snapshot.snapshot_id,
        evidence="clear frame",
        score=0.95,
    )

    db_session.add(link)
    db_session.commit()

    saved_scene = db_session.query(Scene).filter_by(scene_id=scene.scene_id).one()

    assert len(saved_scene.snapshot_links) == 1
    assert saved_scene.snapshot_links[0].snapshot_id == snapshot.snapshot_id


def test_narrative_jsonb_roundtrip(db_session):
    job = VideoJob(job_id="job4", status="created")
    db_session.add(job)
    db_session.flush()

    narrative = Narrative(
        job_id=job.job_id,
        short_summary="Short",
        full_story="Full story",
        structured_data={"characters": ["Alice"], "events": 3},
    )

    db_session.add(narrative)
    db_session.commit()

    saved = db_session.query(Narrative).filter_by(job_id=job.job_id).one()

    assert saved.structured_data["characters"] == ["Alice"]
    assert saved.structured_data["events"] == 3


def test_cascade_delete_job(db_session):
    job = VideoJob(job_id="job5", status="created")

    asset = VideoAsset(
        job_id=job.job_id,
        uri="/tmp/video.mp4",
    )

    db_session.add_all([job, asset])
    db_session.commit()

    db_session.delete(job)
    db_session.commit()

    remaining = db_session.query(VideoAsset).filter_by(job_id="job5").all()

    assert remaining == []