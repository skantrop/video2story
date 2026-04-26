from pathlib import Path
import pytest

from app.pipeline.extract import extract_preprocess_persist_snapshots
from app.persistence.tables import Snapshot, VideoAsset


def test_extract_pipeline_happy_path(
    db_session,
    job,
    video_asset,
    snapshot_config,
    tmp_path,
    mocker,
):
    snapshots_dir = tmp_path / "jobs" / job.job_id / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    fake_files = []
    for i in range(3):
        f = snapshots_dir / f"{i+1:06d}.jpg"
        f.touch()
        fake_files.append(f)

    mocker.patch("app.pipeline.extract._run_ffmpeg_extract")
    mocker.patch(
        "app.pipeline.extract._sorted_frame_files",
        return_value=fake_files,
    )
    mocker.patch(
        "app.pipeline.extract._process_frame",
        return_value=(256, 128),
    )

    result = extract_preprocess_persist_snapshots(
        job_id=job.job_id,
        db=db_session,
        storage_root=tmp_path,
    )

    saved = (
        db_session.query(Snapshot)
        .filter_by(job_id=job.job_id)
        .order_by(Snapshot.timestamp_sec.asc())
        .all()
    )

    assert len(result.files) == 3
    assert result.fps == 2.0
    assert result.snapshots_dir == snapshots_dir

    assert len(saved) == 3

    assert saved[0].timestamp_sec == 0.0
    assert saved[1].timestamp_sec == 0.5
    assert saved[2].timestamp_sec == 1.0

    assert saved[0].width == 256
    assert saved[0].height == 128


def test_extract_raises_if_video_missing(
    db_session,
    job,
    snapshot_config,
    tmp_path,
):
    asset = VideoAsset(
        job_id=job.job_id,
        uri=str(tmp_path / "missing.mp4"),
    )
    db_session.add(asset)
    db_session.commit()

    with pytest.raises(FileNotFoundError):
        extract_preprocess_persist_snapshots(
            job_id=job.job_id,
            db=db_session,
            storage_root=tmp_path,
        )


def test_extract_handles_failed_frame_processing(
    db_session,
    job,
    video_asset,
    snapshot_config,
    tmp_path,
    mocker,
):
    snapshots_dir = tmp_path / "jobs" / job.job_id / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    f = snapshots_dir / "000001.jpg"
    f.touch()

    mocker.patch("app.pipeline.extract._run_ffmpeg_extract")
    mocker.patch(
        "app.pipeline.extract._sorted_frame_files",
        return_value=[f],
    )
    mocker.patch(
        "app.pipeline.extract._process_frame",
        return_value=(None, None),
    )

    extract_preprocess_persist_snapshots(
        job_id=job.job_id,
        db=db_session,
        storage_root=tmp_path,
    )

    saved = db_session.query(Snapshot).filter_by(job_id=job.job_id).one()

    assert saved.width is None
    assert saved.height is None


def test_extract_handles_no_frames(
    db_session,
    job,
    video_asset,
    snapshot_config,
    tmp_path,
    mocker,
):
    """
    If ffmpeg runs but no frames are produced,
    the pipeline should raise a RuntimeError
    (treated as corrupted/invalid video).
    """

    # Mock ffmpeg run (does nothing)
    mocker.patch("app.pipeline.extract._run_ffmpeg_extract")

    # Mock no frames returned
    mocker.patch(
        "app.pipeline.extract._sorted_frame_files",
        return_value=[],
    )

    # Expect failure
    with pytest.raises(RuntimeError, match="Frame extraction failed"):
        extract_preprocess_persist_snapshots(
            job_id=job.job_id,
            db=db_session,
            storage_root=tmp_path,
        )

    # Ensure nothing was written to DB
    saved = db_session.query(Snapshot).filter_by(job_id=job.job_id).all()
    assert saved == []