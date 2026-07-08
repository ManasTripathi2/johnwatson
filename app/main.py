from fastapi import FastAPI

from app.api.health import router as health_router

from app.api.interview import router as interview_router

from app.api.replay import router as replay_router

app = FastAPI(
    title="JohnWatson",
    description="AI-powered interview participant identification system.",
    version="1.0.0",
)

app.include_router(health_router)

app.include_router(
    interview_router
)

app.include_router(
    replay_router
)

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Welcome to JohnWatson"
    }