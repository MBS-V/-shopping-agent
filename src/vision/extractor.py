import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION")

# Connect using the new Google Gen AI SDK
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=REGION
)

def extract_attributes(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    """
    Sends an image to Gemini 2.0 Flash.
    Returns product attributes as a dictionary.
    """
    prompt = """
    Look at this product image and extract attributes.
    Return ONLY a JSON object with these keys:
    - category (e.g. shoes, shirt, bag)
    - colour (main colour)
    - style (e.g. casual, formal, sporty)
    - material (if visible, otherwise unknown)
    - gender (men, women, unisex)
    - brand (if visible, otherwise unknown)

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
    # Remove markdown if Gemini adds it
    raw = raw.replace("```json", "").replace("```", "").strip()
    attributes = json.loads(raw)
    return attributes