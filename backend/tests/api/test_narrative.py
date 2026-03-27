import pytest
from app.persistence.tables import Scene


def test_get_narrative_not_exists(client, job):
    res = client.get(f"/jobs/{job.job_id}/narrative")

    assert res.status_code == 200
    assert res.json()["exists"] is False


def test_generate_narrative(client, db_session, job, mocker):
    # create scene
    scene = Scene(
        job_id=job.job_id,
        start_sec=0,
        end_sec=5,
        short_description="Person enters room",
        confidence=0.9,
    )
    db_session.add(scene)
    db_session.commit()

    # mock LLM
    mocker.patch(
        "app.api.routes.narrative.generate_narrative_from_scenes",
        return_value=type(
            "Result",
            (),
            {
                "narrative": "Full story",
                "summary": "Short summary",
                "structured": {"events": 1},
            },
        )(),
    )

    res = client.post(f"/jobs/{job.job_id}/narrative/generate")

    assert res.status_code == 200

    data = res.json()
    assert data["status"] == "generated"
    assert data["narrative"]["short_summary"] == "Short summary"


def test_generate_narrative_no_scenes(client, job):
    res = client.post(f"/jobs/{job.job_id}/narrative/generate")

    assert res.status_code == 400