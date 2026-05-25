# vector_store.py
# In-memory vector search.
# Embeds all products once, then finds the most similar ones
# to a query using cosine similarity (comparing number lists).

import math
from src.search.embedder import get_text_embedding, product_to_text, attributes_to_text
from src.search.catalogue import CATALOGUE

def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Measures how similar two embeddings are.
    Returns a number between 0 and 1.
    1.0 = identical, 0.0 = completely different.
    """
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def build_catalogue_index() -> list:
    """
    Embeds every product in the catalogue.
    Returns a list of (product, embedding) pairs.
    This runs once when the app starts.
    """
    print("Building catalogue index...")
    index = []
    for product in CATALOGUE:
        text = product_to_text(product)
        embedding = get_text_embedding(text)
        index.append((product, embedding))
        print(f"  Indexed: {product['name']}")
    print("Index complete.")
    return index

def find_similar_products(attributes: dict, index: list, top_k: int = 5) -> list:
    """
    Takes extracted image attributes, converts to embedding,
    compares against all indexed products, returns top 5 matches.
    """
    # Convert uploaded image attributes to text then embedding
    query_text = attributes_to_text(attributes)
    query_embedding = get_text_embedding(query_text)

    # Score every product in the catalogue
    scored = []
    for product, product_embedding in index:
        score = cosine_similarity(query_embedding, product_embedding)
        scored.append((score, product))

    # Sort by score descending, return top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [product for score, product in scored[:top_k]]