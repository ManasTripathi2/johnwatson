from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.interview import router as interview_router
from app.api.replay import router as replay_router
from app.api.confidence import router as confidence_router
from app.api.dashboard import router as dashboard_router
from app.api.ml import router as ml_router

app = FastAPI(
    title="JohnWatson",
    description="Explainable interview participant identification system.",
    version="1.0.0",
)

dashboard_path = Path(__file__).resolve().parents[1] / "dashboard"
app.mount(
    "/static",
    StaticFiles(directory=dashboard_path / "static"),
    name="static",
)

app.include_router(health_router)
app.include_router(interview_router)
app.include_router(replay_router)
app.include_router(confidence_router)
app.include_router(ml_router)
app.include_router(dashboard_router)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to JohnWatson"
    }
