from pathlib import Path

from app.pipeline.extract import extract_preprocess_persist_snapshots

def test_extract_creates_snapshot_files(
    db_session,
    job,
    video_asset,
    snapshot_config,
    tmp_path,
    mocker,
):
    snapshots_dir = tmp_path / "jobs" / job.job_id / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    def fake_ffmpeg(video_path, out_pattern, fps):
        for i in range(3):
            f = snapshots_dir / f"{i+1:06d}.jpg"
            f.write_bytes(b"fake image data")

    mocker.patch("app.pipeline.extract._run_ffmpeg_extract", side_effect=fake_ffmpeg)

    mocker.patch(
        "app.pipeline.extract._process_frame",
        return_value=(256, 128),
    )

    result = extract_preprocess_persist_snapshots(
        job_id=job.job_id,
        db=db_session,
        storage_root=tmp_path,
    )

    for f in result.files:
        assert f.exists()

    assert len(list(snapshots_dir.glob("*.jpg"))) == 3