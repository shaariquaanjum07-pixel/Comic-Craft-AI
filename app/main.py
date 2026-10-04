from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routes import router
from app.services.image_generator import IMAGE_DIR

settings = get_settings()

app = FastAPI(
    title="ComicCraft API",
    description="AI comic story creator using Gemini-compatible text generation and Stable Diffusion-compatible image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.mount("/generated_images", StaticFiles(directory=str(IMAGE_DIR)), name="generated_images")
app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app_mode": settings.app_mode,
        "image_mode": settings.image_mode,
        "gemini_configured": bool(settings.gemini_api_key),
    }
