from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
from sqlalchemy.orm import Session

from app.persistence.tables import Snapshot, SnapshotConfig, VideoAsset

DEFAULT_RESIZE_WIDTH = 512  # fallback if UI does not provide one

@dataclass(frozen=True)
class ExtractResult:
    files: list[Path]
    fps: float
    snapshots_dir: Path


def _run_ffmpeg_extract(video_path: Path, out_pattern: Path, sampling_fps: float) -> None:
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video_path), "-vf", f"fps={sampling_fps}", str(out_pattern),
    ]
    subprocess.run(cmd, check=True)


def _sorted_frame_files(snapshots_dir: Path, image_format: str) -> list[Path]:
    files = list(snapshots_dir.glob(f"*.{image_format}"))
    
    def extract_number(p: Path):
        match = re.search(r"(\d+)", p.stem)
        return int(match.group(1)) if match else p.stem
    
    return sorted(files, key=extract_number)


def _process_frame(path: Path, cfg: SnapshotConfig):
    img = cv2.imread(str(path))
    if img is None:
        return None, None

    if cfg.black_white:
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    elif cfg.grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    target_w = cfg.resize_width or DEFAULT_RESIZE_WIDTH
    h, w = img.shape[:2]
    if w != target_w and w > 0 and target_w > 0:
        ratio = target_w / w
        new_h = max(1, int(h * ratio))
        img = cv2.resize(img, (target_w, new_h))

    cv2.imwrite(str(path), img)
    return img.shape[1], img.shape[0]  # width x height


def extract_preprocess_persist_snapshots(
    job_id: str,
    db: Session,
    storage_root: Path,
) -> ExtractResult:
    cfg = db.query(SnapshotConfig).filter_by(job_id=job_id).one()
    asset = db.query(VideoAsset).filter_by(job_id=job_id).one()

    video_path = Path(asset.uri)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found at: {video_path}")

    snapshots_dir = storage_root / "jobs" / job_id / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    out_pattern = snapshots_dir / f"%06d.{cfg.image_format}"
    _run_ffmpeg_extract(video_path, out_pattern, float(cfg.sampling_fps))

    files = _sorted_frame_files(snapshots_dir, cfg.image_format)

    for i, f in enumerate(files):
        width, height = _process_frame(f, cfg)
        timestamp_sec = i / float(cfg.sampling_fps)

        db.add(Snapshot(
            job_id=job_id,
            timestamp_sec=timestamp_sec,
            uri=str(f),
            width=width,
            height=height,
        ))
    
    db.commit()
    return ExtractResult(files, float(cfg.sampling_fps), snapshots_dir)