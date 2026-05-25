import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION")

client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)

def get_mime_type(image_bytes: bytes) -> str:
    """
    Detects image format automatically using Pillow.
    No more manual file extension checking.
    """
    img = Image.open(io.BytesIO(image_bytes))
    fmt = img.format.lower()
    mapping = {"jpeg": "image/jpeg", "jpg": "image/jpeg",
               "png": "image/png", "webp": "image/webp"}
    return mapping.get(fmt, "image/jpeg")

def extract_attributes(image_bytes: bytes, mime_type: str = None) -> dict:
    """
    Sends image to Gemini 2.5 Flash.
    Returns product attributes as a clean dictionary.
    Falls back to unknown values if Gemini returns bad JSON.
    """
    # Auto-detect mime type if not provided
    if mime_type is None:
        mime_type = get_mime_type(image_bytes)

    prompt = """
    Look at this product image and extract attributes.
    Return ONLY a JSON object with these exact keys:
    - category (e.g. shoes, shirt, bag)
    - colour (main colour)
    - style (e.g. casual, formal, sporty, luxury)
    - material (if visible, otherwise unknown)
    - gender (men, women, unisex)
    - brand (if visible, otherwise unknown)
    - confidence (your overall confidence as a percentage integer e.g. 92)

    Return only the JSON. No explanation. No markdown.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt
        ]
    )

    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    # Error handling — if Gemini returns bad JSON, return safe defaults
    try:
        attributes = json.loads(raw)
    except json.JSONDecodeError:
        attributes = {
            "category": "unknown",
            "colour": "unknown",
            "style": "unknown",
            "material": "unknown",
            "gender": "unknown",
            "brand": "unknown",
            "confidence": 0
        }

    return attributes