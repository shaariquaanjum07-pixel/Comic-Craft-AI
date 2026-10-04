from __future__ import annotations

from app.schemas import ComicPanel, PanelOutline, PanelStory


def build_comic_layout(
    outlines: list[PanelOutline],
    stories: list[PanelStory],
    image_paths: list[tuple[str, str]],
) -> list[ComicPanel]:
    if not (len(outlines) == len(stories) == len(image_paths)):
        raise ValueError("Outline, story, and image counts must match.")

    story_by_panel = {story.panel_number: story for story in stories}
    layout: list[ComicPanel] = []

    for outline, (image_url, image_disk_path) in zip(outlines, image_paths, strict=True):
        story = story_by_panel.get(outline.panel_number)
        if story is None:
            raise ValueError(f"Missing story for panel {outline.panel_number}.")

        layout.append(
            ComicPanel(
                panel_number=outline.panel_number,
                title=outline.title,
                scene_description=outline.scene_description,
                image_prompt=outline.image_prompt,
                image_url=image_url,
                image_disk_path=image_disk_path,
                caption=story.caption,
                narration=story.narration,
                dialogue=story.dialogue,
            )
        )

    return layout
