# graph.py
# Defines the LangGraph agent.
# LangGraph lets you build agents as a graph of nodes.
# Each node is a step. Edges connect steps.
# The agent can loop, branch, and decide what to do next.

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from src.agent.tools import (
    search_similar_products,
    filter_by_price,
    get_recommendation
)

# ─── Agent State ────────────────────────────────────────────────
# This dictionary is passed between every node in the graph.
# Each node reads from it and writes back to it.
class AgentState(TypedDict):
    attributes: dict          # Gemini extracted attributes
    index: list               # product catalogue index
    max_price: Optional[int]  # optional price filter
    products: list            # search results
    recommendation: str       # final plain-English recommendation
    steps_taken: list         # tracks which tools were called

# ─── Node 1: Search ─────────────────────────────────────────────
def search_node(state: AgentState) -> AgentState:
    """Calls Tool 1 — finds similar products."""
    print("Agent Node 1: Searching catalogue...")
    products = search_similar_products(
        state["attributes"],
        state["index"],
        top_k=5
    )
    return {**state, "products": products, 
            "steps_taken": state.get("steps_taken", []) + ["search"]}

# ─── Node 2: Price Filter ───────────────────────────────────────
def price_filter_node(state: AgentState) -> AgentState:
    """Calls Tool 2 — filters by price if max_price is set."""
    if state.get("max_price"):
        print(f"Agent Node 2: Filtering by ₹{state['max_price']}...")
        filtered = filter_by_price(state["products"], state["max_price"])
        # Keep original results if filter removes everything
        products = filtered if filtered else state["products"]
    else:
        print("Agent Node 2: No price filter set, skipping...")
        products = state["products"]
    return {**state, "products": products,
            "steps_taken": state.get("steps_taken", []) + ["price_filter"]}

# ─── Node 3: Recommend ──────────────────────────────────────────
def recommend_node(state: AgentState) -> AgentState:
    """Calls Tool 3 — generates plain-English recommendation."""
    print("Agent Node 3: Generating recommendation...")
    recommendation = get_recommendation(
        state["attributes"],
        state["products"]
    )
    return {**state, "recommendation": recommendation,
            "steps_taken": state.get("steps_taken", []) + ["recommend"]}

# ─── Build the Graph ────────────────────────────────────────────
def build_agent() -> StateGraph:
    """
    Assembles the agent graph.
    Nodes = steps. Edges = connections between steps.
    This is what makes it a LangGraph agent.
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("search", search_node)
    graph.add_node("price_filter", price_filter_node)
    graph.add_node("recommend", recommend_node)

    # Connect nodes in order
    # search → price_filter → recommend → END
    graph.set_entry_point("search")
    graph.add_edge("search", "price_filter")
    graph.add_edge("price_filter", "recommend")
    graph.add_edge("recommend", END)

    return graph.compile()

# Single agent instance reused across calls
agent = build_agent()

def run_agent(attributes: dict, index: list, max_price: int = None) -> dict:
    """
    Runs the full LangGraph agent pipeline.
    Input: image attributes + catalogue index + optional price filter
    Output: products + recommendation + steps taken
    """
    initial_state = {
        "attributes": attributes,
        "index": index,
        "max_price": max_price,
        "products": [],
        "recommendation": "",
        "steps_taken": []
    }

    result = agent.invoke(initial_state)

    return {
        "products": result["products"],
        "recommendation": result["recommendation"],
        "steps_taken": result["steps_taken"],
        "total_found": len(result["products"])
    }