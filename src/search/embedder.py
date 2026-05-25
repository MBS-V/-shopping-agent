# embedder.py
# Converts product text attributes into embeddings (lists of numbers).
# Similar products will have similar numbers.
# We use Vertex AI text embeddings — same Google infrastructure as Gemini.

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
REGION = os.getenv("GCP_REGION")

client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)

def get_text_embedding(text: str) -> list:
    """
    Converts a text string into a list of numbers (embedding).
    Example: "black formal shoes" → [0.12, 0.87, 0.34, ...]
    """
    response = client.models.embed_content(
        model="text-embedding-005",
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
    )
    return response.embeddings[0].values

def product_to_text(product: dict) -> str:
    """
    Converts a product dictionary into a searchable text string.
    Example: {"category": "shoes", "colour": "black"} 
          → "shoes black formal patent leather men unknown"
    """
    return f"{product.get('category', '')} {product.get('colour', '')} {product.get('style', '')} {product.get('material', '')} {product.get('gender', '')} {product.get('brand', '')}"

def attributes_to_text(attributes: dict) -> str:
    """
    Same as product_to_text but for Gemini's extracted attributes.
    We use this to convert the uploaded image's attributes into
    a text string we can embed and search with.
    """
    return product_to_text(attributes)