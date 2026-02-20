from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.routes.jobs import router as jobs_router

app = FastAPI()

STORAGE_ROOT = Path(__file__).resolve().parents[1] / "storage"
app.mount("/storage", StaticFiles(directory=str(STORAGE_ROOT)), name="storage")

app.include_router(jobs_router)