from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.comic_service import generate_comic
from app.services.image_generator import generate_image

settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))
router = APIRouter()


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_mode": settings.app_mode, "image_mode": settings.image_mode},
    )


@router.post("/generate")
def generate_from_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        result = generate_comic(payload)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": result.layout,
                "pdf_url": result.pdf_url,
                "pdf_filename": result.pdf_filename,
                "character_name": payload.character_name,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            status_code=500,
            context={"message": str(exc)},
        )


@router.post("/generate-comic/json")
def generate_from_json(payload: PromptRequest):
    try:
        return generate_comic(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/test-image")
def test_image(prompt: str = Query("A cheerful robot reading a comic book")):
    try:
        image_url, image_disk_path = generate_image(prompt, panel_number=0)
        return {"prompt": prompt, "image_url": image_url, "image_disk_path": image_disk_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
def download_pdf(filename: str):
    safe_name = Path(filename).name
    file_path = settings.exports_dir / safe_name
    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get("/export-success")
def export_success(request: Request, pdf: str | None = None):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"pdf": pdf},
    )
