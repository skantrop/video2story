from app.persistence.tables import VideoJob


def test_can_insert_job(db_session):
    job = VideoJob(job_id="job-test", status="created")
    db_session.add(job)
    db_session.commit()

    saved = db_session.query(VideoJob).filter_by(job_id="job-test").one()

    assert saved.status == "created"