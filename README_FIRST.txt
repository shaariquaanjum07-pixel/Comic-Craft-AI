COMICCRAFT - QUICK START

1. Extract this ZIP.
2. Open the extracted ComicCraft folder in VS Code.
3. Make sure Python 3.11 or newer is installed.
4. EASIEST WINDOWS METHOD: double-click START_PROJECT.bat.
5. Or use VS Code Terminal:

   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload

6. Open http://127.0.0.1:8000

The included .env is already configured for DEMO MODE, so you can test the complete
website, five-panel generation, images, preview, and PDF export without an API key.

After the demo works, edit .env to connect Gemini. Stable Diffusion is optional and
requires the larger AI dependency set; see README.md.
