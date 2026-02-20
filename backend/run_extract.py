from pathlib import Path

from app.persistence.db import SessionLocal
from app.pipeline.extract import extract_preprocess_persist_snapshots


JOB_ID = "dd212389-8454-4a1e-a9e3-67e2fc185bfc"

STORAGE_ROOT = Path(__file__).resolve().parent / "storage"


def main():
    db = SessionLocal()
    result = extract_preprocess_persist_snapshots(JOB_ID, db, STORAGE_ROOT)

    print("Saved frames:", len(result.files))
    print("Snapshots dir:", result.snapshots_dir)


if __name__ == "__main__":
    main()