from app.persistence.tables import Snapshot, SnapshotConfig


def test_build_scenes(client, db_session, job):
    # config
    cfg = SnapshotConfig(
        job_id=job.job_id,
        sampling_fps=1.0,
        chunk_length_sec=5,
        resize_width=256,
        grayscale=False,
        black_white=False,
        image_format="jpg",
    )
    db_session.add(cfg)

    # snapshots
    snaps = [
        Snapshot(job_id=job.job_id, timestamp_sec=i, uri=f"/tmp/{i}.jpg")
        for i in range(10)
    ]
    db_session.add_all(snaps)
    db_session.commit()

    res = client.post(f"/jobs/{job.job_id}/scenes/build")

    assert res.status_code == 200
    assert res.json()["status"] == "scenes_built"


def test_list_scenes(client, job):
    res = client.get(f"/jobs/{job.job_id}/scenes")

    assert res.status_code == 200
    assert "scenes" in res.json()


def test_get_scene_not_found(client, job):
    res = client.get(f"/jobs/{job.job_id}/scenes/does-not-exist")

    assert res.status_code == 404


def test_describe_scene(client, db_session, job, mocker):
    from app.persistence.tables import Scene, SceneSnapshot, Snapshot

    # snapshot
    snap = Snapshot(job_id=job.job_id, timestamp_sec=0, uri="/tmp/1.jpg")
    db_session.add(snap)
    db_session.flush()

    # scene
    scene = Scene(
        job_id=job.job_id,
        start_sec=0,
        end_sec=5,
        short_description="(pending)",
    )
    db_session.add(scene)
    db_session.flush()

    db_session.add(SceneSnapshot(scene_id=scene.scene_id, snapshot_id=snap.snapshot_id))
    db_session.commit()

    # mock VLM
    mocker.patch(
        "app.api.routes.scenes.describe_scene_hf",
        return_value=type(
            "Result",
            (),
            {"text": "A person walking", "confidence": 0.8},
        )(),
    )

    res = client.post(f"/jobs/{job.job_id}/scenes/{scene.scene_id}/describe")

    assert res.status_code == 200
    assert res.json()["short_description"] == "A person walking"