from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

base_dir = Path(__file__).resolve().parents[2]
index_file = base_dir / "dashboard" / "index.html"

@router.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(index_file.read_text(encoding="utf-8"))
