# tools.py
# Defines the tools the LangGraph agent can use.
# Each tool is a plain Python function.
# The agent decides which ones to call based on the user's query.

import json
from src.search.vector_store import find_similar_products
from src.search.catalogue import CATALOGUE

def search_similar_products(attributes: dict, index: list, top_k: int = 5) -> list:
    """
    Tool 1: Finds similar products from the catalogue.
    Input: extracted image attributes
    Output: list of matching products
    """
    return find_similar_products(attributes, index, top_k)

def filter_by_price(products: list, max_price: int) -> list:
    """
    Tool 2: Filters products by maximum price.
    Input: list of products, max price in rupees
    Output: filtered list
    """
    return [p for p in products if p['price'] <= max_price]

def get_recommendation(attributes: dict, products: list) -> str:
    """
    Tool 3: Generates a plain-English recommendation.
    Input: detected attributes + matched products
    Output: recommendation string
    """
    if not products:
        return "No matching products found in our catalogue for your image."

    top = products[0]
    others = products[1:3]

    recommendation = f"Based on your image, I detected a **{attributes.get('colour', '')} "
    recommendation += f"{attributes.get('style', '')} {attributes.get('category', '')}**. "
    recommendation += f"\n\n🏆 **Best match:** {top['name']} at ₹{top['price']}. "

    if others:
        other_names = " and ".join([f"{p['name']} (₹{p['price']})" for p in others])
        recommendation += f"\n\n🔍 **Also consider:** {other_names}."

    if attributes.get('brand', 'unknown') != 'unknown':
        recommendation += f"\n\n💡 **Tip:** You searched for {attributes.get('brand')} — "
        recommendation += "we've shown you similar style alternatives."

    return recommendation

def run_agent_pipeline(attributes: dict, index: list, max_price: int = None) -> dict:
    """
    The main agent pipeline.
    Runs all 3 tools in sequence and returns a complete result.
    This is what LangGraph orchestrates in a real agent.
    """
    # Tool 1: Search
    print("Agent: Running Tool 1 — searching similar products...")
    similar = search_similar_products(attributes, index, top_k=5)

    # Tool 2: Price filter (only if max_price set)
    if max_price:
        print(f"Agent: Running Tool 2 — filtering by max price ₹{max_price}...")
        similar = filter_by_price(similar, max_price)

    # Tool 3: Recommendation
    print("Agent: Running Tool 3 — generating recommendation...")
    recommendation = get_recommendation(attributes, similar)

    return {
        "products": similar,
        "recommendation": recommendation,
        "tools_used": ["search", "price_filter" if max_price else None, "recommendation"],
        "total_found": len(similar)
    }