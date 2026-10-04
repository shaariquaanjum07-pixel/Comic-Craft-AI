from __future__ import annotations

import logging
import math
import os
import urllib.parse
import uuid
import time
import requests
from PIL import Image, ImageDraw

logger = logging.getLogger("comiccraft.image_generator")

# Folder where generated images will be saved
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "generated_images")
os.makedirs(IMAGE_DIR, exist_ok=True)


def _render_fallback_comic_panel(
    output_path: str,
    panel_number: int = 1,
    prompt: str = "",
    character_name: str = "",
    setting: str = "",
    tone: str = "mysterious",
    art_style: str = "classic comic book",
    width: int = 512,
    height: int = 512,
) -> None:
    """Generate a stylized comic panel illustration with Pillow if online AI is rate-limited or unavailable."""
    tone_palettes = {
        "mysterious": ((24, 20, 48), (68, 42, 104), (138, 86, 186), (255, 216, 74)),
        "dramatic": ((38, 14, 22), (124, 28, 42), (218, 64, 52), (255, 225, 96)),
        "funny": ((255, 244, 214), (255, 184, 56), (244, 88, 76), (25, 25, 30)),
        "light-hearted": ((228, 246, 255), (96, 180, 242), (76, 198, 154), (28, 44, 68)),
        "poetic": ((242, 232, 248), (156, 122, 184), (92, 68, 134), (244, 212, 116)),
    }
    bg_top, bg_mid, bg_accent, ink_color = tone_palettes.get(
        tone.lower(), ((26, 32, 54), (64, 82, 134), (132, 164, 220), (255, 216, 74))
    )

    im = Image.new("RGB", (width, height), bg_top)
    draw = ImageDraw.Draw(im)

    # Vertical atmospheric gradient
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(bg_top[0] + (bg_mid[0] - bg_top[0]) * ratio)
        g = int(bg_top[1] + (bg_mid[1] - bg_top[1]) * ratio)
        b = int(bg_top[2] + (bg_mid[2] - bg_top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Comic sunburst / action rays
    center_x, center_y = width // 2, int(height * 0.44)
    num_rays = 20
    for ray in range(num_rays):
        if ray % 2 == 0:
            a1 = (ray / num_rays) * 2 * math.pi
            a2 = ((ray + 0.85) / num_rays) * 2 * math.pi
            x1 = center_x + math.cos(a1) * width
            y1 = center_y + math.sin(a1) * height
            x2 = center_x + math.cos(a2) * width
            y2 = center_y + math.sin(a2) * height
            draw.polygon([(center_x, center_y), (x1, y1), (x2, y2)], fill=bg_accent)

    # Comic dot pattern (halftone simulation)
    for x in range(24, width - 24, 18):
        for y in range(24, height - 24, 18):
            if (x + y) % 36 == 0:
                draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=bg_accent)

    # Setting silhouette horizon
    horizon_y = int(height * 0.64)
    draw.rectangle([0, horizon_y, width, height], fill=(16, 18, 26))

    # Stylized character silhouette
    char_top = int(height * 0.34)
    head_radius = 52
    draw.ellipse(
        [center_x - head_radius, char_top - head_radius, center_x + head_radius, char_top + head_radius],
        fill=(244, 218, 186),
        outline=(20, 20, 20),
        width=4,
    )
    # Character body/torso
    draw.polygon(
        [
            (center_x - 85, horizon_y + 10),
            (center_x - 52, char_top + 45),
            (center_x + 52, char_top + 45),
            (center_x + 85, horizon_y + 10),
        ],
        fill=(36, 46, 68),
        outline=(20, 20, 20),
        width=4,
    )

    # Comic frames: outer bold border, inner border
    margin = 12
    draw.rectangle([margin, margin, width - margin, height - margin], outline=(20, 20, 20), width=6)
    draw.rectangle([margin + 6, margin + 6, width - margin - 6, height - margin - 6], outline=(255, 255, 255), width=2)

    # Panel number badge
    badge_w, badge_h = 125, 34
    draw.rectangle(
        [margin + 10, margin + 10, margin + 10 + badge_w, margin + 10 + badge_h],
        fill=(255, 216, 74),
        outline=(20, 20, 20),
        width=3,
    )
    draw.text((margin + 20, margin + 18), f"PANEL {panel_number}", fill=(20, 20, 20))

    # Art style badge
    if art_style:
        style_label = art_style[:20].upper()
        style_w = len(style_label) * 8 + 20
        draw.rectangle(
            [width - margin - 10 - style_w, margin + 10, width - margin - 10, margin + 10 + badge_h],
            fill=(25, 25, 35),
            outline=(255, 216, 74),
            width=2,
        )
        draw.text((width - margin - 10 - style_w + 10, margin + 18), style_label, fill=(255, 216, 74))

    # Bottom caption / setting strip
    banner_y = height - margin - 58
    draw.rectangle(
        [margin + 10, banner_y, width - margin - 10, height - margin - 10],
        fill=(255, 250, 240),
        outline=(20, 20, 20),
        width=3,
    )
    char_display = character_name or "Hero"
    set_display = setting or "Scene"
    draw.text((margin + 20, banner_y + 8), f"{char_display} in {set_display}", fill=(20, 20, 20))
    prompt_snippet = (prompt[:55] + "...") if len(prompt) > 55 else prompt
    draw.text((margin + 20, banner_y + 26), f"Scene: {prompt_snippet}", fill=(70, 70, 70))

    im.save(output_path, "PNG")


def generate_image(
    prompt: str,
    panel_number: int = 1,
    art_style: str = "",
    character_name: str = "",
    setting: str = "",
    tone: str = "",
    *args,
    **kwargs,
) -> tuple[str, str]:
    """
    Generate an AI comic panel image and save it locally to IMAGE_DIR.

    Returns:
        image_url: URL to display the image in the browser (e.g. /generated_images/comic_panel_1_abc.png)
        image_disk_path: Valid, non-None local file path of the downloaded image file on disk.
    """
    clean_prompt = str(prompt).strip()

    # Pass panel_number if supplied via args or kwargs
    if args and isinstance(args[0], int):
        panel_number = args[0]
    if "panel_number" in kwargs:
        panel_number = int(kwargs["panel_number"])

    art_style = art_style or kwargs.get("art_style", "")
    character_name = character_name or kwargs.get("character_name", "")
    setting = setting or kwargs.get("setting", "")
    tone = tone or kwargs.get("tone", "")

    # Ensure style, character, tone, and setting are integrated into the visual prompt
    full_prompt = clean_prompt
    if art_style and art_style.lower() not in full_prompt.lower():
        full_prompt = f"{art_style} comic style, {full_prompt}"
    if character_name and character_name.lower() not in full_prompt.lower():
        full_prompt = f"{full_prompt}, featuring character {character_name}"
    if setting and setting.lower() not in full_prompt.lower():
        full_prompt = f"{full_prompt}, setting: {setting}"
    if tone and tone.lower() not in full_prompt.lower():
        full_prompt = f"{full_prompt}, tone: {tone}"

    encoded_prompt = urllib.parse.quote(full_prompt, safe="")

    # Unique seed for each panel to ensure distinct scenes
    seed = (abs(hash(f"{character_name}_{setting}_{tone}_{art_style}")) % 100000) + int(panel_number)

    # Unique filename per panel
    unique_id = uuid.uuid4().hex[:8]
    filename = f"comic_panel_{panel_number}_{unique_id}.png"
    image_disk_path = os.path.join(IMAGE_DIR, filename)
    local_image_url = f"/generated_images/{filename}"

    # Pollinations AI URL
    api_url = (
        f"https://image.pollinations.ai/prompt/"
        f"{encoded_prompt}"
        f"?width=512"
        f"&height=512"
        f"&seed={seed}"
        f"&nologo=true"
    )

    headers = {
        "User-Agent": f"ComicCraft/1.0 (Windows; Panel {panel_number})"
    }

    # Attempt online generation with retry
    success = False
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=35)
            if response.status_code == 200 and len(response.content) >= 1000:
                with open(image_disk_path, "wb") as f:
                    f.write(response.content)
                logger.info("Panel %s image downloaded successfully to %s", panel_number, image_disk_path)
                print(f"Panel {panel_number} image downloaded successfully: {image_disk_path}")
                success = True
                break
            elif response.status_code in (402, 429):
                logger.warning(
                    "Pollinations returned status %s for panel %s (attempt %s/%s).",
                    response.status_code,
                    panel_number,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(2)
        except Exception as exc:
            logger.warning("Pollinations request error for panel %s: %s", panel_number, exc)
            time.sleep(1)

    # Fallback to visual comic illustration if online provider fails or rate-limits
    if not success:
        logger.info("Creating stylized visual comic art for panel %s at %s", panel_number, image_disk_path)
        try:
            _render_fallback_comic_panel(
                output_path=image_disk_path,
                panel_number=panel_number,
                prompt=clean_prompt,
                character_name=character_name,
                setting=setting,
                tone=tone,
                art_style=art_style,
            )
            print(f"Panel {panel_number} comic illustration created locally: {image_disk_path}")
        except Exception as render_err:
            logger.error("Failed to render comic art panel: %s", render_err)
            raise RuntimeError(f"Could not generate panel image: {render_err}") from render_err

    # GUARANTEE: image_disk_path is ALWAYS a valid string pointing to an existing file
    if not os.path.exists(image_disk_path):
        raise RuntimeError(f"Image file does not exist at {image_disk_path}")

    return local_image_url, image_disk_path


def generate_panel_image(prompt: str, *args, **kwargs) -> tuple[str, str]:
    """Generate a comic panel image."""
    return generate_image(prompt, *args, **kwargs)