from pathlib import Path


def test_create_job(client, tmp_path, monkeypatch):
    # override storage root to tmp
    monkeypatch.setattr(
        "app.api.routes.jobs.STORAGE_ROOT",
        tmp_path,
    )

    files = {
        "video": ("test.mp4", b"fake video content", "video/mp4"),
    }

    data = {
        "sampling_fps": "2.0",
        "chunk_length_sec": "10",
        "resize_width": "256",
        "grayscale": "false",
        "black_white": "false",
        "image_format": "jpg",
        "run_extract": "false",
    }

    response = client.post("/jobs", files=files, data=data)

    assert response.status_code == 200

    body = response.json()

    assert "job_id" in body
    assert body["status"] == "uploaded"

    # check file exists
    job_id = body["job_id"]
    expected_path = tmp_path / "jobs" / job_id / "video"
    assert expected_path.exists()


def test_list_jobs(client):
    response = client.get("/jobs")

    assert response.status_code == 200
    assert "jobs" in response.json()


def test_get_job_not_found(client):
    response = client.get("/jobs/nonexistent")

    assert response.status_code == 404


def test_get_job(client, db_session, job):
    response = client.get(f"/jobs/{job.job_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == job.job_id


def test_delete_job(client, db_session, job, tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.jobs.STORAGE_ROOT",
        tmp_path,
    )

    # create fake directory
    job_dir = tmp_path / "jobs" / job.job_id
    job_dir.mkdir(parents=True)

    response = client.delete(f"/jobs/{job.job_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

    assert not job_dir.exists()


def test_delete_job_not_found(client):
    response = client.delete("/jobs/nonexistent")

    assert response.status_code == 404