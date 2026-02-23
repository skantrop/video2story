from pathlib import Path

import uuid
import shutil
from fastapi import File, Form, UploadFile
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.persistence.db import get_db, SessionLocal
from app.persistence.tables import Snapshot, SnapshotConfig, VideoAsset, VideoJob
from app.pipeline.extract import extract_preprocess_persist_snapshots

router = APIRouter(prefix="/jobs", tags=["jobs"])

# backend/storage
STORAGE_ROOT = Path(__file__).resolve().parents[3] / "storage"


def _run_extract_job(job_id: str) -> None:
    """
    Background task entrypoint.
    Create a fresh DB session here (do NOT reuse request-scoped session).
    """
    db = SessionLocal()
    try:
        extract_preprocess_persist_snapshots(job_id, db, STORAGE_ROOT)
    finally:
        db.close()


@router.get("")
def list_jobs(db: Session = Depends(get_db)):
    """
    List jobs for sidebar: id, status, created_at, snapshot_count.
    """
    rows = (
        db.query(
            VideoJob.job_id,
            VideoJob.status,
            VideoJob.created_at,
            func.count(Snapshot.snapshot_id).label("snapshot_count"),
        )
        .outerjoin(Snapshot, Snapshot.job_id == VideoJob.job_id)
        .group_by(VideoJob.job_id)
        .order_by(VideoJob.created_at.desc())
        .all()
    )

    return {
        "jobs": [
            {
                "job_id": r.job_id,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "snapshot_count": int(r.snapshot_count or 0),
            }
            for r in rows
        ]
    }


@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    Job detail: status, created_at, video uri, config, snapshot_count.
    """
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    asset = db.query(VideoAsset).filter_by(job_id=job_id).first()
    cfg = db.query(SnapshotConfig).filter_by(job_id=job_id).first()

    snapshot_count = (
        db.query(func.count(Snapshot.snapshot_id))
        .filter(Snapshot.job_id == job_id)
        .scalar()
    )

    return {
        "job_id": job.job_id,
        "status": job.status,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "video_uri": asset.uri if asset else None,
        "snapshot_count": int(snapshot_count or 0),
        "config": None
        if not cfg
        else {
            "sampling_fps": float(cfg.sampling_fps),
            "chunk_length_sec": cfg.chunk_length_sec,
            "resize_width": cfg.resize_width,
            "grayscale": bool(cfg.grayscale),
            "black_white": bool(cfg.black_white),
            "image_format": cfg.image_format,
        },
    }


@router.get("/{job_id}/snapshots")
def list_snapshots(job_id: str, db: Session = Depends(get_db)):
    """
    List snapshots for a job. Returns URLs under /storage/... for <img src>.
    """
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
        # Snapshot.uri is typically an absolute path to a file under STORAGE_ROOT.
        p = Path(s.uri)

        # Convert absolute file path -> relative -> URL under /storage
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
def run_extract(job_id: str, background: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger extraction in the background.
    (Optional) checks job exists first.
    """
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    background.add_task(_run_extract_job, job_id)
    return {"job_id": job_id, "status": "extraction_started"}

def _save_upload(upload: UploadFile, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("wb") as f:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


@router.post("")
def create_job(
    background: BackgroundTasks,
    db: Session = Depends(get_db),

    # uploaded video
    video: UploadFile = File(...),

    # config fields from UI
    sampling_fps: float = Form(1.0),
    chunk_length_sec: int = Form(10),
    resize_width: int = Form(512),
    grayscale: bool = Form(False),
    black_white: bool = Form(False),
    image_format: str = Form("jpg"),

    # workflow toggle
    run_extract: bool = Form(True),
):
    job_id = str(uuid.uuid4())

    # 1) create job
    job = VideoJob(job_id=job_id, status="uploaded")
    db.add(job)

    # 2) save video file into storage/jobs/<job_id>/video/original.<ext>
    ext = "mp4"
    if video.filename and "." in video.filename:
        ext = video.filename.rsplit(".", 1)[-1].lower()

    video_path = STORAGE_ROOT / "jobs" / job_id / "video" / f"original.{ext}"
    try:
        _save_upload(video, video_path)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    # 3) persist video asset row
    db.add(
        VideoAsset(
            video_id=str(uuid.uuid4()),
            job_id=job_id,
            uri=str(video_path),
        )
    )

    # 4) persist snapshot config row
    db.add(
        SnapshotConfig(
            config_id=str(uuid.uuid4()),
            job_id=job_id,
            sampling_fps=sampling_fps,
            chunk_length_sec=chunk_length_sec,
            resize_width=resize_width,
            grayscale=grayscale,
            black_white=black_white,
            image_format=image_format,
        )
    )

    db.commit()

    # 5) optionally run extraction in background
    if run_extract:
        background.add_task(_run_extract_job, job_id)

    return {
        "job_id": job_id,
        "status": "extracting" if run_extract else "uploaded",
        "video_url": f"/storage/jobs/{job_id}/video/{video_path.name}",
    }

@router.delete("/{job_id}")
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

    job_dir = STORAGE_ROOT / "jobs" / job_id
    shutil.rmtree(job_dir, ignore_errors=True)

    return {"job_id": job_id, "status": "deleted"}