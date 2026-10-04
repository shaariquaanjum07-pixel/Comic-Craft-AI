from __future__ import annotations

import json

from app.config import get_settings
from app.schemas import ComicStory, PanelOutline, PanelStory, PromptRequest


def _demo_story(request: PromptRequest, outlines: list[PanelOutline]) -> list[PanelStory]:
    demo_dialogues = [
        f'{request.character_name}: "What is this doing here? There is no return address or name on it..."',
        f'{request.character_name}: "Wait... the watch is ticking steadily counter-clockwise!"',
        f'{request.character_name}: "\'Do not fix the clock, or Tuesday will never happen.\' This is my own handwriting!"',
        f'{request.character_name}: "The shadows are twisting unnaturally. Time itself is starting to fracture!"',
        f'{request.character_name}: "Whatever happens next, I have to make the choice right now!"',
    ]
    stories: list[PanelStory] = []
    for idx, panel in enumerate(outlines):
        diag = demo_dialogues[idx % len(demo_dialogues)]
        stories.append(
            PanelStory(
                panel_number=panel.panel_number,
                caption=f"Panel {panel.panel_number}: {panel.title}",
                narration=(
                    f"In {request.setting}, {request.character_name} confronts the unfolding mystery with a {request.tone} resolve. "
                    f"{panel.scene_description}"
                ),
                dialogue=diag,
            )
        )
    return stories


def generate_story(request: PromptRequest, outlines: list[PanelOutline]) -> list[PanelStory]:
    """Expand outlines into narration, caption, and dialogue for each panel, falling back automatically on 429 quota exhaustion."""
    import logging
    logger = logging.getLogger("comiccraft.gemini_pro")
    settings = get_settings()

    if settings.app_mode.lower() == "demo" or not settings.gemini_api_key:
        return _demo_story(request, outlines)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        outline_json = json.dumps([p.model_dump() for p in outlines], ensure_ascii=False)
        prompt = f"""
Write the story content for this comic.

Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Original story idea: {request.story_prompt}
Panel outline JSON: {outline_json}

Return one story object for every panel, preserving the same panel_number.
Each panel needs:
- caption: 1 short atmospheric line
- narration: 2-4 concise sentences advancing the plot
- dialogue: 1-3 natural dialogue lines suitable for a comic
Avoid markdown. Keep character continuity across all panels.
""".strip()

        response = client.models.generate_content(
            model=settings.gemini_story_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicStory,
                temperature=0.9,
            ),
        )

        parsed = ComicStory.model_validate_json(response.text)
        stories = parsed.panels
        if len(stories) != len(outlines):
            raise ValueError("Gemini story panel count does not match the outline panel count.")
        stories.sort(key=lambda p: p.panel_number)
        return stories

    except Exception as exc:
        logger.warning(
            "Gemini story generation encountered an issue or quota exhaustion (429): %s. Triggering fallback story.",
            exc,
        )
        print(f"[Gemini Story Fallback] Handled error / 429 quota exhaustion: {exc}")
        return _demo_story(request, outlines)
