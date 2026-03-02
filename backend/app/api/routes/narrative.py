from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.persistence.db import get_db
from app.persistence.tables import Narrative, Scene, VideoJob
from app.services.llm.hf_text_client import generate_narrative_from_scenes

router = APIRouter(prefix="/jobs", tags=["narrative"])


def _scene_line(s: Scene) -> str:
    start = float(s.start_sec or 0)
    end = float(s.end_sec or 0)
    desc = (s.short_description or "").strip()
    return f"{start:.0f}-{end:.0f}s: {desc}"


@router.get("/{job_id}/narrative")
def get_narrative(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    n = db.query(Narrative).filter_by(job_id=job_id).first()
    if not n:
        return {"job_id": job_id, "exists": False, "narrative": None}

    return {
        "job_id": job_id,
        "exists": True,
        "narrative": {
            "short_summary": n.short_summary,
            "full_story": n.full_story,
            "structured_data": n.structured_data,
        },
    }


@router.post("/{job_id}/narrative/generate")
def generate_narrative(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    scenes = (
        db.query(Scene)
        .filter(Scene.job_id == job_id)
        .order_by(Scene.start_sec.asc())
        .all()
    )

    usable = [
        s
        for s in scenes
        if s.short_description
        and s.short_description.strip()
        and s.short_description.strip() != "(pending)"
    ]

    if not usable:
        raise HTTPException(
            status_code=400,
            detail="No described scenes found. Describe scenes first (short_description != '(pending)').",
        )

    lines = [_scene_line(s) for s in usable]
    result = generate_narrative_from_scenes(lines)

    n = db.query(Narrative).filter_by(job_id=job_id).first()
    if not n:
        n = Narrative(job_id=job_id)

    n.full_story = result.narrative
    n.short_summary = result.summary
    n.structured_data = result.structured

    db.add(n)
    db.commit()
    db.refresh(n)

    return {
        "job_id": job_id,
        "status": "generated",
        "narrative": {
            "short_summary": n.short_summary,
            "full_story": n.full_story,
            "structured_data": n.structured_data,
        },
    }