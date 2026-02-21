from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.persistence.db import get_db, SessionLocal
from app.persistence.tables import Snapshot, VideoJob
from app.pipeline.extract import extract_preprocess_persist_snapshots

router = APIRouter(prefix="/jobs", tags=["jobs"])

STORAGE_ROOT = Path(__file__).resolve().parents[3] / "storage"


def _run_extract_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        extract_preprocess_persist_snapshots(job_id, db, STORAGE_ROOT)
    finally:
        db.close()


@router.get("/{job_id}/snapshots")
def list_snapshots(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    snaps = (
        db.query(Snapshot)
        .filter(Snapshot.job_id == job_id)
        .order_by(Snapshot.timestamp_sec.asc())
        .all()
    )

    out = []
    for s in snaps:
        p = Path(s.uri)

        rel = p.relative_to(STORAGE_ROOT)
        url = f"/storage/{rel.as_posix()}"

        out.append(
            {
                "snapshot_id": s.snapshot_id,
                "timestamp_sec": s.timestamp_sec,
                "url": url,
                "width": s.width,
                "height": s.height,
            }
        )

    return {"job_id": job_id, "count": len(out), "snapshots": out}


@router.post("/{job_id}/extract")
def run_extract(job_id: str, background: BackgroundTasks):
    background.add_task(_run_extract_job, job_id)
    return {"job_id": job_id, "status": "extraction_started"}