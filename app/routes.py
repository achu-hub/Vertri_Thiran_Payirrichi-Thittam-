from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .gemini import generate_comic_story, generate_panel_image

router = APIRouter(prefix="/api", tags=["ComicCraft"])

GENERATED_DIR = Path(__file__).resolve().parent.parent / "generated"


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=2000)
    genre: str = Field(default="Adventure", max_length=100)
    characters: str = Field(default="", max_length=2000)
    panels: int = Field(default=6, ge=1, le=12)


class ImageRequest(BaseModel):
    panel_number: int = Field(..., ge=1, le=12)
    description: str = Field(..., min_length=3, max_length=5000)


@router.get("/health")
def health():
    return {"status": "ok", "service": "ComicCraft API"}


@router.post("/generate")
def generate(request: GenerateRequest):
    try:
        result = generate_comic_story(
            prompt=request.prompt,
            genre=request.genre,
            characters=request.characters,
            panels=request.panels,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/generate-image")
def generate_image(request: ImageRequest):
    try:
        filename = generate_panel_image(
            image_prompt=request.description,
            output_dir=GENERATED_DIR,
            panel_number=request.panel_number,
        )
        return {
            "success": True,
            "filename": filename,
            "url": f"/generated/{filename}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
