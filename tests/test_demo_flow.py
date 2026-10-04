from pathlib import Path

from fastapi.testclient import TestClient

from app.config import get_settings

# Settings are read lazily. The project's .env.example defaults to demo mode;
# if a user has a real .env, these endpoint tests still only assert basic behavior.
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text


def test_demo_json_generation(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "app_mode", "demo")
    monkeypatch.setattr(settings, "image_mode", "demo")

    payload = {
        "story_prompt": "A brave fox explores an enchanted forest and finds a glowing key.",
        "character_name": "Fino",
        "setting": "Enchanted forest",
        "tone": "funny",
        "art_style": "classic comic book",
    }
    response = client.post("/generate-comic/json", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["layout"]) == settings.num_panels
    assert data["pdf_filename"].endswith(".pdf")
    assert (settings.exports_dir / data["pdf_filename"]).exists()
    for panel in data["layout"]:
        assert Path(panel["image_disk_path"]).exists()
