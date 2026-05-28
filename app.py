import streamlit as st
from PIL import Image
import io
import json
import sys
import os
sys.path.append('.')
from src.vision.extractor import extract_attributes
from src.search.vector_store import build_catalogue_index, find_similar_products
from src.agent.graph import run_agent

st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon=None,
    layout="centered"
)

# ─── Cache index ────────────────────────────────────────────────
@st.cache_resource(show_spinner="Building product index ...") # Cache the index to speed up repeated searches,happens only once on app load or when code changes
def load_index():
    return build_catalogue_index()

@st.cache_data
def cached_search(_index, attributes_str, top_k=5):
    attributes = json.loads(attributes_str)
    return find_similar_products(attributes, _index, top_k)

index = load_index()

# ─── Header ─────────────────────────────────────────────────────
st.title("AI Shopping Agent")
st.caption("Upload a product image to find similar items.")
st.divider()

# ─── Search history sidebar ──────────────────────────────────────
with st.sidebar:
    st.header("Search History")
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if st.session_state["history"]:
        for i, h in enumerate(reversed(st.session_state["history"][-5:])):
            st.markdown(f"**{i+1}.** {h['category']} · {h['colour']}")
    else:
        st.caption("Your recent searches will appear here.")

# ─── Upload ─────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png", "webp"]
)

# ─── Price filter slider ─────────────────────────────────────────
max_price = st.slider(
    "Maximum price (Rs.)",
    min_value=500,
    max_value=20000,
    value=20000,
    step=500,
    help="Drag to filter results by price"
)

if uploaded_file is not None:
    image_bytes = uploaded_file.read()

    # Smart mime detection
    image = Image.open(io.BytesIO(image_bytes))
    fmt = image.format.lower() if image.format else "jpeg"
    mime_type = "image/jpeg" if fmt == "jpg" else f"image/{fmt}"

    st.image(image, caption="Uploaded image", use_container_width=True)
    st.divider()

    if st.button("Find Similar Products", type="primary", use_container_width=True):
        with st.spinner("Analysing image..."):
            try:
                # Step 1: Extract attributes from image
                attributes = extract_attributes(image_bytes, mime_type=mime_type)

                # Step 2: Run LangGraph agent pipeline
                result = run_agent(
                    attributes=attributes,
                    index=index,
                    max_price=max_price if max_price < 20000 else None
                )

                # Step 3: Save to search history
                st.session_state["history"].append({
                    "category": attributes.get("category", "unknown"),
                    "colour": attributes.get("colour", "unknown")
                })

                # ─── Results ────────────────────────────────────
                st.success("Analysis complete.")

                # Confidence bar
                confidence = attributes.get("confidence", 0)
                st.caption(f"Gemini confidence: {confidence}%")
                st.progress(confidence / 100)

                # Detected attributes grid
                st.subheader("Detected Attributes")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Category", attributes.get("category", "Unknown").title())
                    st.metric("Colour", attributes.get("colour", "Unknown").title())
                    st.metric("Style", attributes.get("style", "Unknown").title())
                with col2:
                    st.metric("Material", attributes.get("material", "Unknown").title())
                    st.metric("Gender", attributes.get("gender", "Unknown").title())
                    st.metric("Brand", attributes.get("brand", "Unknown").title())

                st.divider()

                # Agent recommendation
                st.subheader("Recommendation")
                st.markdown(result["recommendation"])
                st.caption(f"Agent steps: {' → '.join([s for s in result['steps_taken'] if s])}")

                st.divider()

                # Similar products grid
                st.subheader("Similar Products")

                if max_price < 20000:
                    st.caption(f"Showing results under Rs.{max_price}")

                products = result["products"]

                if not products:
                    st.warning(
                        "No similar products found in our catalogue for this image. "
                        "Try uploading a fashion product like shoes, clothing, or accessories."
                    )
                else:
                    cols = st.columns(3)
                    for i, product in enumerate(products):
                        with cols[i % 3]:
                            st.image(product['image_url'], use_container_width=True)
                            st.markdown(f"**{product['name']}**")
                            st.markdown(f"Rs.{product['price']}")
                            st.caption(
                                f"{product['style'].title()} · {product['colour'].title()}"
                            )

                st.divider()

                st.info(
                    "This catalogue contains 2,638 fashion products across 143 categories. "
                    "Results are ranked by visual similarity using text embeddings."
                )

                with st.expander("Raw JSON from Gemini"):
                    st.json(attributes)

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                st.markdown("Check your .env file and GCP project settings.")

else:
    st.markdown(
        """
        <div style='text-align: center; padding: 40px; 
        border: 2px dashed #cccccc; border-radius: 10px; color: #888888;'>
            <h3>No image uploaded yet</h3>
            <p>Drag and drop a product image above to get started</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
