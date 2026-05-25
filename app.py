import streamlit as st
from PIL import Image
import io
import json
import sys
sys.path.append('.')
from src.vision.extractor import extract_attributes
from src.search.vector_store import build_catalogue_index, find_similar_products

st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon="🛍️",
    layout="centered"
)

# Cache the catalogue index — builds once, reused forever
@st.cache_resource
def load_index():
    return build_catalogue_index()

# Cache search results — same query doesn't hit API twice
@st.cache_data
def cached_search(_index, attributes_str, top_k=5):
    attributes = json.loads(attributes_str)
    return find_similar_products(attributes, _index, top_k)

index = load_index()

# ─── Header ────────────────────────────────────────────────────
st.title("🛍️ AI Shopping Agent")
st.markdown("Upload a product image to find similar items instantly.")
st.divider()

# ─── Upload ────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png", "webp"]
)

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption="Uploaded image", use_container_width=True)
    st.divider()

    if st.button("🔍 Find Similar Products", type="primary", use_container_width=True):
        with st.spinner("Gemini is analysing your image..."):
            try:
                # Step 1: Extract attributes
                attributes = extract_attributes(image_bytes)
                st.success("Image analysed!")

                # Step 2: Show attributes + confidence
                st.subheader("📋 Detected Attributes")

                # Confidence bar
                confidence = attributes.get("confidence", 0)
                st.markdown(f"**Gemini Confidence:** {confidence}%")
                st.progress(confidence / 100)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Category", attributes.get("category", "Unknown"))
                    st.metric("Colour", attributes.get("colour", "Unknown"))
                    st.metric("Style", attributes.get("style", "Unknown"))
                with col2:
                    st.metric("Material", attributes.get("material", "Unknown"))
                    st.metric("Gender", attributes.get("gender", "Unknown"))
                    st.metric("Brand", attributes.get("brand", "Unknown"))

                st.divider()

                # Step 3: Find similar products (cached)
                st.subheader("🛍️ Similar Products Found")
                attributes_str = json.dumps(attributes)
                similar = cached_search(index, attributes_str, top_k=5)

                cols = st.columns(3)
                for i, product in enumerate(similar):
                    with cols[i % 3]:
                        st.image(product['image_url'], use_container_width=True)
                        st.markdown(f"**{product['name']}**")
                        st.markdown(f"₹{product['price']}")
                        st.markdown(f"`{product['style']}` · `{product['colour']}`")

                st.divider()
                with st.expander("🔧 Raw JSON from Gemini"):
                    st.json(attributes)

                st.session_state['last_attributes'] = attributes
                st.session_state['last_image'] = image_bytes

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                st.markdown("**Common fixes:**")
                st.markdown("- Check your internet connection")
                st.markdown("- Make sure your .env file has the correct Project ID")
                st.markdown("- Check GCP Console that Vertex AI API is enabled")

else:
    st.markdown(
        """
        <div style='text-align: center; padding: 40px; 
        border: 2px dashed #cccccc; border-radius: 10px; color: #888888;'>
            <h3>📸 No image uploaded yet</h3>
            <p>Drag and drop a product image above to get started</p>
        </div>
        """,
        unsafe_allow_html=True
    )