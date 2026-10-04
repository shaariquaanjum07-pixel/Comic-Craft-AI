**# ComicCraft - AI Comic Story Creator**

ComicCraft is a FastAPI + Jinja2 web application that turns a user's story prompt into a five-panel comic, generates narration/dialogue, creates one image per panel, previews the result in a browser, and exports the comic to PDF.

This implementation follows the project documentation's architecture, while making the AI providers configurable so the app can still be tested before API keys or large Stable Diffusion model downloads are set up.

**## Project structure**

\`\`\`text

comiccraft_complete/

├── app/

│   ├── main.py

│   ├── routes.py

│   ├── config.py

│   ├── schemas.py

│   └── services/

│       ├── comic_service.py

│       ├── gemini_flash.py

│       ├── gemini_pro.py

│       ├── image_generator.py

│       ├── layout_builder.py

│       └── exporters.py

├── templates/

│   ├── index.html

│   ├── comic_preview\.html

│   ├── export_success.html

│   └── error.html

├── static/

│   ├── css/styles.css

│   ├── panels/

│   └── exports/

├── tests/test_demo_flow\.py

├── .env.example

├── requirements.txt

├── requirements-ai.txt

└── README.md

\`\`\`

**## 1. Open in VS Code**

1\. Extract/open the \`comiccraft_complete\` folder.

2\. Open VS Code.

3\. Choose **\*\*File > Open Folder\*\*** and select \`comiccraft_complete\`.

4\. Open **\*\*Terminal > New Terminal\*\***.

**## 2. Create a virtual environment**

**### Windows PowerShell**

\`\`\`powershell

py -m venv .venv

.\\.venv\Scripts\Activate.ps1

\`\`\`

If PowerShell blocks activation, run this once in that terminal:

\`\`\`powershell

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\\.venv\Scripts\Activate.ps1

\`\`\`

**### Windows Command Prompt**

\`\`\`bat

py -m venv .venv

.venv\Scripts\activate

\`\`\`

**### macOS/Linux**

\`\`\`bash

python3 -m venv .venv

source .venv/bin/activate

\`\`\`

**## 3. Install the normal dependencies**

\`\`\`bash

python -m pip install --upgrade pip

pip install -r requirements.txt

\`\`\`

This is enough to run the complete website in **\*\*demo mode\*\***.

**## 4. Create your \`.env\`**

Copy \`.env.example\` to \`.env\`.

Windows Command Prompt:

\`\`\`bat

copy .env.example .env

\`\`\`

PowerShell:

\`\`\`powershell

Copy-Item .env.example .env

\`\`\`

macOS/Linux:

\`\`\`bash

cp .env.example .env

\`\`\`

Keep this first test configuration:

\`\`\`env

APP_MODE=demo

IMAGE_MODE=demo

\`\`\`

Demo mode creates deterministic story text and placeholder panel art. This lets you test the entire FastAPI/Jinja2/PDF pipeline without API keys.

**## 5. Run the project**

\`\`\`bash

uvicorn app.main\:app --reload

\`\`\`

Open:

\- App: \`[http://127.0.0.1:8000](http://127.0.0.1:8000)\`

\- API docs: \`[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)\`

\- Health check: \`[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)\`

**## 6. Test the complete flow**

In the browser:

1\. Enter a story prompt.

2\. Enter a character name.

3\. Choose setting, tone, and art style.

4\. Click **\*\*Generate My Comic\*\***.

5\. Check all five panels.

6\. Click **\*\*Download Your Comic as PDF\*\***.

7\. The PDF downloads and the browser opens the export-success page.

You can also test JSON generation at \`/docs\` using \`POST /generate-comic/json\`.

Example JSON body:

\`\`\`json

{

  "story_prompt": "A brave fox explores an enchanted forest and discovers a glowing key.",

  "character_name": "Fino",

  "setting": "Enchanted forest",

  "tone": "funny",

  "art_style": "classic comic book"

}

\`\`\`

**## 7. Turn on real Gemini text generation**

Get a Gemini API key from Google AI Studio, then edit \`.env\`:

\`\`\`env

APP_MODE=ai

GEMINI_API_KEY=PASTE_YOUR_REAL_KEY_HERE

GEMINI_OUTLINE_MODEL=gemini-3.8-flash

GEMINI_STORY_MODEL=gemini-3.8-flash

IMAGE_MODE=demo

\`\`\`

Restart Uvicorn after changing \`.env\`.

The project uses the current \`google-genai\` Python package and structured JSON responses. The model names are environment variables, so they can be changed later without editing Python files.

**## 8. Turn on local Stable Diffusion images**

**\*\*Important:\*\*** local Stable Diffusion is much heavier than the normal web app. A supported NVIDIA GPU is strongly recommended. CPU generation can be very slow.

Install the optional AI stack:

\`\`\`bash

pip install -r requirements-ai.txt

\`\`\`

Then edit \`.env\`:

\`\`\`env

IMAGE_MODE=diffusers

SD_MODEL_ID=stable-diffusion-v1-5/stable-diffusion-v1-5

HF_TOKEN=

\`\`\`

If the model repository requires authentication on your machine, put your Hugging Face token in \`HF_TOKEN\`.

Restart:

\`\`\`bash

uvicorn app.main\:app --reload

\`\`\`

The first Stable Diffusion run downloads model files and can use several GB of disk space.

**## 9. Run automated tests**

Install pytest:

\`\`\`bash

pip install pytest

\`\`\`

Then run:

\`\`\`bash

pytest -q

\`\`\`

The test suite checks the homepage, health route, complete demo JSON generation, generated panel files, and generated PDF.

**## Main routes**

\| Route | Method | Purpose |

\|---|---|---|

\| \`/\` | GET | Homepage and form |

\| \`/generate\` | POST | Form-based full comic generation |

\| \`/generate-comic/json\` | POST | JSON API full comic generation |

\| \`/test-image\` | GET | Generate/test one image |

\| \`/download/{filename}\` | GET | Download generated PDF |

\| \`/export-success\` | GET | Export confirmation page |

\| \`/health\` | GET | Configuration/health check |

\| \`/docs\` | GET | FastAPI Swagger interface |

**## Common beginner errors**

**### \`ModuleNotFoundError\`**

Make sure the virtual environment is activated, then run:

\`\`\`bash

pip install -r requirements.txt

\`\`\`

**### \`uvicorn is not recognized\`**

Use:

\`\`\`bash

python -m uvicorn app.main\:app --reload

\`\`\`

**### Gemini API error**

Check that \`.env\` contains a valid \`GEMINI_API_KEY\`, then restart Uvicorn. If a model name becomes unavailable, replace the values of \`GEMINI_OUTLINE_MODEL\` and \`GEMINI_STORY_MODEL\` with a model currently supported by your Gemini API account.

**### Stable Diffusion is too slow / crashes**

Set:

\`\`\`env

IMAGE_MODE=demo

\`\`\`

The rest of the application will continue working. You can demonstrate backend routing, frontend rendering, story flow, image slots, and PDF export using demo mode.

**## Notes about the original documentation**

The supplied report describes Gemini 1.5 Flash/Pro and \`runwayml/stable-diffusion-v1-5\`. This project keeps the same functional roles but makes model IDs configurable. That avoids hard-coding a retired/changed API model into the project.