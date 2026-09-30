# ComicCraft - AI Comic Story Creator

ComicCraft is a FastAPI + HTML/CSS/JavaScript application that uses Google's Gemini API to:
1. Generate a comic story from a topic/prompt.
2. Break the story into comic panels.
3. Generate an image for an individual panel.
4. Display the generated comic in a simple browser UI.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   └── gemini.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── generated/
│   └── .gitkeep
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Open the project in VS Code

Open the `ComicCraft` folder.

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.env\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
venv\Scripts\activate
```

## 3. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Add your Gemini API key

Open `.env` and replace:

```text
GEMINI_API_KEY=YOUR_REAL_KEY
```

with your real key.

Do not put the key inside frontend JavaScript. Do not commit `.env` to Git.

## 5. Run

```bash
python -m uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## API endpoints

- `GET /api/health`
- `POST /api/generate`
- `POST /api/generate-image`

### Generate story request

```json
{
  "prompt": "A young inventor discovers a robot in an old workshop.",
  "genre": "Adventure",
  "characters": "Arun, a curious student; Robo, a friendly robot",
  "panels": 6
}
```

### Generate image request

```json
{
  "panel_number": 1,
  "description": "Arun discovers a glowing robot inside an old workshop."
}
```

## Notes

The Gemini model names are configurable in `.env`. If Google changes model availability, change `GEMINI_TEXT_MODEL` or `GEMINI_IMAGE_MODEL` there rather than changing the frontend.

Image generation requires a Gemini model/account that supports image generation.
