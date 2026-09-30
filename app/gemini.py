import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

_client = genai.Client(api_key=API_KEY) if API_KEY else None


def ensure_client():
    if not API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Open the .env file and add your Gemini API key."
        )
    return _client


def _extract_json(text: str):
    text = (text or "").strip()

    # Remove Markdown code fences if Gemini returns them.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find the first JSON object.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return json.loads(text[start:end + 1])

    raise ValueError("Gemini returned an invalid JSON response.")


def generate_comic_story(prompt: str, genre: str, characters: str, panels: int):
    client = ensure_client()

    system_instruction = """
You are ComicCraft, an expert comic-book story writer.
Create a coherent short comic story and divide it into the requested number of panels.
Keep characters visually consistent across panels.
Return ONLY valid JSON with this exact structure:
{
  "title": "string",
  "summary": "string",
  "panels": [
    {
      "panel_number": 1,
      "scene": "short visual scene description",
      "caption": "short narration caption",
      "dialogue": [
        {"speaker": "character", "text": "dialogue"}
      ],
      "image_prompt": "detailed image-generation prompt"
    }
  ]
}
Do not include Markdown fences.
"""

    user_prompt = f"""
Create a comic with:
Topic/story idea: {prompt}
Genre: {genre}
Characters: {characters or "Create suitable characters"}
Number of panels: {panels}

Make the plot have a beginning, development, and ending.
Use concise dialogue suitable for comic speech bubbles.
Make every image_prompt describe the same characters consistently.
"""

    response = client.models.generate_content(
        model=TEXT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.8,
        ),
    )

    data = _extract_json(response.text)

    if not isinstance(data, dict) or not isinstance(data.get("panels"), list):
        raise ValueError("Gemini response did not contain a panels list.")

    return data


def generate_panel_image(image_prompt: str, output_dir: Path, panel_number: int):
    client = ensure_client()

    prompt = f"""
Create a single comic-book panel illustration.

{image_prompt}

Requirements:
- clean comic-book composition
- expressive characters
- clear foreground and background
- consistent character appearance
- suitable for a family-friendly comic
- no speech bubbles or written dialogue in the image
- landscape 4:3 composition
"""

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    for part in response.parts:
        if getattr(part, "inline_data", None) is not None:
            image = part.as_image()
            filename = f"panel_{panel_number}.png"
            path = output_dir / filename
            image.save(path)
            return filename

    raise RuntimeError("Gemini did not return an image for this panel.")
