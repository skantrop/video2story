from __future__ import annotations

import math
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.persistence.db import get_db
from app.persistence.tables import (
    VideoJob,
    Snapshot,
    SnapshotConfig,
    Scene,
    SceneSnapshot,
)

router = APIRouter(prefix="/jobs", tags=["scenes"])

# backend/storage
STORAGE_ROOT = Path(__file__).resolve().parents[3] / "storage"

DEFAULT_KEYFRAMES = 8


def _storage_url_from_snapshot_uri(uri: str) -> str:
    """
    Convert absolute file path under STORAGE_ROOT to URL like:
    /storage/jobs/<job_id>/snapshots/000001.jpg
    """
    p = Path(uri)
    rel = p.relative_to(STORAGE_ROOT)
    return f"/storage/{rel.as_posix()}"


def _pick_uniform_keyframes(snaps: List[Snapshot], k: int) -> List[Snapshot]:
    """
    Pick k snapshots uniformly from an ordered list.
    """
    if not snaps:
        return []
    if k <= 0:
        return []
    if len(snaps) <= k:
        return snaps

    # indices from 0..n-1 inclusive
    n = len(snaps)
    idxs = [round(i * (n - 1) / (k - 1)) for i in range(k)]
    # remove duplicates while preserving order
    seen = set()
    out = []
    for ix in idxs:
        if ix not in seen:
            out.append(snaps[ix])
            seen.add(ix)
    return out


@router.post("/{job_id}/scenes/build")
def build_scenes(job_id: str, db: Session = Depends(get_db)):
    """
    Baseline scene segmentation: fixed time chunks using SnapshotConfig.chunk_length_sec.
    Rebuilds scenes for this job (idempotent).
    """
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cfg = db.query(SnapshotConfig).filter_by(job_id=job_id).first()
    if not cfg:
        raise HTTPException(status_code=400, detail="SnapshotConfig not found for job")

    chunk = int(cfg.chunk_length_sec or 0)
    if chunk <= 0:
        raise HTTPException(status_code=400, detail="chunk_length_sec must be > 0")

    # Make sure we actually have snapshots
    max_ts = db.query(func.max(Snapshot.timestamp_sec)).filter(Snapshot.job_id == job_id).scalar()
    if max_ts is None:
        raise HTTPException(status_code=400, detail="No snapshots found for job. Run extraction first.")

    # ----- delete existing scenes for job (rebuild) -----
    existing_scene_ids = [sid for (sid,) in db.query(Scene.scene_id).filter(Scene.job_id == job_id).all()]
    if existing_scene_ids:
        db.query(SceneSnapshot).filter(SceneSnapshot.scene_id.in_(existing_scene_ids)).delete(synchronize_session=False)
        db.query(Scene).filter(Scene.job_id == job_id).delete(synchronize_session=False)
        db.commit()

    # ----- build new scenes -----
    total_duration = float(max_ts)
    num_scenes = int(math.floor(total_duration / chunk)) + 1

    created = 0
    for i in range(num_scenes):
        start_sec = i * chunk
        end_sec = (i + 1) * chunk

        # snapshots within [start, end)
        snaps = (
            db.query(Snapshot)
            .filter(Snapshot.job_id == job_id)
            .filter(Snapshot.timestamp_sec >= start_sec)
            .filter(Snapshot.timestamp_sec < end_sec)
            .order_by(Snapshot.timestamp_sec.asc())
            .all()
        )

        # skip empty scenes to keep UI clean
        if not snaps:
            continue

        scene_id = str(uuid.uuid4())
        scene = Scene(
            scene_id=scene_id,
            job_id=job_id,
            start_sec=float(start_sec),
            end_sec=float(end_sec),
            short_description="(pending)",
            confidence=None,
        )
        db.add(scene)

        for s in snaps:
            db.add(SceneSnapshot(scene_id=scene_id, snapshot_id=s.snapshot_id))

        created += 1

    db.commit()
    return {"job_id": job_id, "status": "scenes_built", "scenes_created": created}


@router.get("/{job_id}/scenes")
def list_scenes(job_id: str, db: Session = Depends(get_db)):
    """
    List scenes with snapshot counts (for the sidebar list).
    """
    job = db.query(VideoJob).filter_by(job_id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    rows = (
        db.query(
            Scene.scene_id,
            Scene.start_sec,
            Scene.end_sec,
            # if your Scene model has description, include it
            getattr(Scene, "description", None),
            func.count(SceneSnapshot.snapshot_id).label("snapshot_count"),
        )
        .outerjoin(SceneSnapshot, SceneSnapshot.scene_id == Scene.scene_id)
        .filter(Scene.job_id == job_id)
        .group_by(Scene.scene_id)
        .order_by(Scene.start_sec.asc())
        .all()
    )

    scenes_out = []
    for r in rows:
        # r[3] might be None if Scene has no description column
        desc = None
        if len(r) >= 4 and isinstance(r[3], str):
            desc = r[3]

        scenes_out.append(
            {
                "scene_id": r[0],
                "start_sec": float(r[1]),
                "end_sec": float(r[2]),
                "snapshot_count": int(r[-1] or 0),
                "description": desc,
            }
        )

    return {"job_id": job_id, "count": len(scenes_out), "scenes": scenes_out}


@router.get("/{job_id}/scenes/{scene_id}")
def get_scene(job_id: str, scene_id: str, keyframes: int = DEFAULT_KEYFRAMES, db: Session = Depends(get_db)):
    """
    Scene detail + keyframes (K uniformly sampled snapshots).
    """
    scene = db.query(Scene).filter_by(scene_id=scene_id, job_id=job_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    snaps = (
        db.query(Snapshot)
        .join(SceneSnapshot, SceneSnapshot.snapshot_id == Snapshot.snapshot_id)
        .filter(SceneSnapshot.scene_id == scene_id)
        .order_by(Snapshot.timestamp_sec.asc())
        .all()
    )

    key_snaps = _pick_uniform_keyframes(snaps, int(keyframes))

    out_keyframes = []
    for s in key_snaps:
        out_keyframes.append(
            {
                "snapshot_id": s.snapshot_id,
                "timestamp_sec": float(s.timestamp_sec),
                "url": _storage_url_from_snapshot_uri(s.uri),
                "width": s.width,
                "height": s.height,
            }
        )

    return {
        "job_id": job_id,
        "scene_id": scene.scene_id,
        "start_sec": float(scene.start_sec),
        "end_sec": float(scene.end_sec),
        "keyframes": out_keyframes,
        "keyframes_count": len(out_keyframes),
        "snapshots_total": len(snaps),
        "description": getattr(scene, "description", None),
    }