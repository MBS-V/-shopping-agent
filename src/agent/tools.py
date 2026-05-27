# tools.py
import json
from src.search.vector_store import find_similar_products
from src.search.catalogue import CATALOGUE

def search_similar_products(attributes: dict, index: list, top_k: int = 5) -> list:
    return find_similar_products(attributes, index, top_k)

def filter_by_price(products: list, max_price: int) -> list:
    filtered = [p for p in products if p['price'] <= max_price]
    return filtered

def get_recommendation(attributes: dict, products: list) -> str:
    """
    Generates a plain, natural recommendation.
    No emojis. No AI-sounding phrases.
    """
    if not products:
        return "No matching products found for your image."

    top = products[0]
    others = products[1:3]

    colour = attributes.get('colour', '')
    style = attributes.get('style', '')
    category = attributes.get('category', '')
    brand = attributes.get('brand', 'unknown')

    rec = f"Detected: {colour} {style} {category}.\n\n"
    rec += f"Top match: {top['name']} at Rs.{top['price']}."

    if others:
        other_names = ", ".join([f"{p['name']} (Rs.{p['price']})" for p in others])
        rec += f"\n\nOther options: {other_names}."

    if brand != 'unknown':
        rec += f"\n\nYou searched for {brand} — showing similar style alternatives."

    return rec

def run_agent_pipeline(attributes: dict, index: list, max_price: int = None) -> dict:
    similar = search_similar_products(attributes, index, top_k=5)
    if max_price:
        filtered = filter_by_price(similar, max_price)
        similar = filtered if filtered else similar
    recommendation = get_recommendation(attributes, similar)
    return {
        "products": similar,
        "recommendation": recommendation,
        "tools_used": ["search", "price_filter" if max_price else None, "recommend"],
        "total_found": len(similar)
    }