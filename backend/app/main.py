from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.jobs import router as jobs_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
STORAGE_ROOT = Path(__file__).resolve().parents[1] / "storage"
app.mount("/storage", StaticFiles(directory=str(STORAGE_ROOT)), name="storage")

app.include_router(jobs_router)