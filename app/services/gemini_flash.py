from __future__ import annotations

from app.config import get_settings
from app.schemas import ComicOutline, PanelOutline, PromptRequest


def _demo_outline(request: PromptRequest, count: int) -> list[PanelOutline]:
    beats = [
        ("The Discovery", "discovers an unexpected mystery item in the setting", "establishing wide shot"),
        ("The Revelation", "investigates closely and uncovers an astonishing secret", "medium shot, expressive reaction"),
        ("The Clue", "finds a critical warning or clue that changes everything", "intense close-up, dramatic lighting"),
        ("The Complication", "grapples with rising tension as reality shifts around them", "dynamic Dutch angle, suspenseful composition"),
        ("The Final Choice", "reaches the dramatic climax with a decisive resolution", "cinematic climax shot, bold contrast"),
    ]
    panels: list[PanelOutline] = []
    for i in range(count):
        title, action, shot = beats[i % len(beats)]
        scene = (
            f"In {request.setting}, {request.character_name} {action}. "
            f"The mood is {request.tone}, following the premise: {request.story_prompt}."
        )
        image_prompt = (
            f"{request.art_style} comic illustration, panel {i + 1}, {shot}. "
            f"{request.character_name} in {request.setting}, {action}. "
            f"Tone: {request.tone}. Clear subject, expressive visual storytelling, cinematic lighting, no text, no watermark"
        )
        panels.append(
            PanelOutline(
                panel_number=i + 1,
                title=title,
                scene_description=scene,
                image_prompt=image_prompt,
            )
        )
    return panels


def generate_outline(request: PromptRequest) -> list[PanelOutline]:
    """Generate a structured comic outline using Gemini, with an automatic fallback on 429 quota exhaustion or API errors."""
    import logging
    logger = logging.getLogger("comiccraft.gemini_flash")
    settings = get_settings()
    count = settings.num_panels

    if settings.app_mode.lower() == "demo" or not settings.gemini_api_key:
        return _demo_outline(request, count)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = f"""
Create exactly {count} progressive comic panels for a visual 5-panel comic story.

Story idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Requirements for visual and narrative consistency:
1. Each of the {count} panels must depict a distinctly different, progressive scene from the story (Panel 1: Beginning/Discovery -> Panel 2: Investigation/Complication -> Panel 3: Crucial Clue/Warning -> Panel 4: Escalation/Crisis -> Panel 5: Climax/Consequence).
2. Maintain character consistency: describe {request.character_name} with the exact same appearance, clothing, and hair in every panel's image_prompt.
3. Maintain setting and style consistency: every panel's image_prompt must specify the art style ({request.art_style}), setting ({request.setting}), and tone ({request.tone}).
4. Image prompts must describe purely visual elements with cinematic camera angles. Specify: no text, no watermarks, no speech bubbles in the image itself.

For every panel return:
- panel_number (integer 1 to {count})
- title
- scene_description
- image_prompt
""".strip()

        response = client.models.generate_content(
            model=settings.gemini_outline_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicOutline,
                temperature=0.8,
            ),
        )

        parsed = ComicOutline.model_validate_json(response.text)
        panels = parsed.panels
        if len(panels) != count:
            raise ValueError(f"Gemini returned {len(panels)} panels; expected {count}.")

        for index, panel in enumerate(panels, start=1):
            panel.panel_number = index
        return panels

    except Exception as exc:
        logger.warning(
            "Gemini outline generation encountered an issue or quota exhaustion (429): %s. Triggering fallback outline.",
            exc,
        )
        print(f"[Gemini Outline Fallback] Handled error / 429 quota exhaustion: {exc}")
        return _demo_outline(request, count)
