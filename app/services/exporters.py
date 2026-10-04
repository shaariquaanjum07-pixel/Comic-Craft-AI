from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import get_settings
from app.schemas import ComicPanel


def _latin_safe(text: str) -> str:
    # Built-in FPDF fonts are Latin-1. Replace unsupported symbols instead of crashing.
    return text.encode("latin-1", errors="replace").decode("latin-1")


def save_pdf(layout: list[ComicPanel], title: str = "ComicCraft Comic") -> tuple[str, str]:
    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"comic_{timestamp}.pdf"
    output_path = settings.exports_dir / filename

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title(_latin_safe(title))

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 10, _latin_safe(f"PANEL {panel.panel_number}: {panel.title.upper()}"))
        pdf.ln(2)

        image_path = Path(panel.image_disk_path).resolve()
        if image_path.exists():
            page_width = pdf.w - pdf.l_margin - pdf.r_margin
            image_width = min(page_width, 160)
            pdf.image(str(image_path), x=(pdf.w - image_width) / 2, w=image_width)
            pdf.ln(5)

        if panel.caption:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _latin_safe(f"CAPTION: {panel.caption}"))
            pdf.ln(1)

        if panel.narration:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, _latin_safe(f"NARRATION: {panel.narration}"))
            pdf.ln(2)

        if panel.dialogue:
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _latin_safe(f"DIALOGUE: {panel.dialogue}"))

    pdf.output(str(output_path))
    return f"/static/exports/{filename}", filename
