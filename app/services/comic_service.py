from __future__ import annotations

from app.schemas import ComicGenerationResult, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


def generate_comic(request: PromptRequest) -> ComicGenerationResult:
    outlines = generate_outline(request)
    stories = generate_story(request, outlines)
    images = [
        generate_image(
            panel.image_prompt,
            panel_number=panel.panel_number,
            art_style=request.art_style,
            character_name=request.character_name,
            setting=request.setting,
            tone=request.tone,
        )
        for panel in outlines
    ]
    layout = build_comic_layout(outlines, stories, images)
    pdf_url, pdf_filename = save_pdf(layout, title=f"{request.character_name}'s Comic")
    return ComicGenerationResult(layout=layout, pdf_url=pdf_url, pdf_filename=pdf_filename)
