# vector_store.py
# Builds a product embedding index and caches it to disk.
# First run: embeds all products and saves to data/index.pkl
# Every run after: loads from disk instantly — no API calls.

import math
import pickle
import os
from src.search.embedder import get_text_embedding, product_to_text, attributes_to_text
from src.search.catalogue import CATALOGUE

INDEX_CACHE_PATH = "data/index.pkl"

def cosine_similarity(vec1: list, vec2: list) -> float:
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def build_catalogue_index(force_rebuild: bool = False) -> list:
    """
    Builds embedding index for all products.
    Saves to disk after first build.
    Loads from disk on every subsequent run — instant.
    force_rebuild=True rebuilds from scratch.
    """
    # Load from cache if it exists
    if os.path.exists(INDEX_CACHE_PATH) and not force_rebuild:
        print("Loading index from cache...")
        with open(INDEX_CACHE_PATH, "rb") as f:
            index = pickle.load(f)
        print(f"Loaded {len(index)} products from cache instantly.")
        return index

    # Build from scratch
    print(f"Building index for {len(CATALOGUE)} products...")
    print("This only happens once — will be cached after this.")
    index = []
    for i, product in enumerate(CATALOGUE):
        text = product_to_text(product)
        embedding = get_text_embedding(text)
        index.append((product, embedding))
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(CATALOGUE)} indexed...")

    # Save to disk
    os.makedirs("data", exist_ok=True)
    with open(INDEX_CACHE_PATH, "wb") as f:
        pickle.dump(index, f)
    print(f"Index saved to {INDEX_CACHE_PATH}")
    return index

def find_similar_products(attributes: dict, index: list, top_k: int = 5) -> list:
    query_text = attributes_to_text(attributes)
    query_embedding = get_text_embedding(query_text)
    scored = []
    for product, product_embedding in index:
        score = cosine_similarity(query_embedding, product_embedding)
        scored.append((score, product))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [product for score, product in scored[:top_k]]