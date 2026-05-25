import streamlit as st
from PIL import Image
import io
import sys
sys.path.append('.')
from src.vision.extractor import extract_attributes
from src.search.vector_store import build_catalogue_index, find_similar_products

st.set_page_config(page_title="AI Shopping Agent", page_icon="🛍️", layout="centered")

# Build catalogue index once when app starts
# st.cache_resource means it only runs once, not on every rerender
@st.cache_resource
def load_index():
    return build_catalogue_index()

index = load_index()

# ─── Header ────────────────────────────────────────────────────
st.title("🛍️ AI Shopping Agent")
st.markdown("Upload a product image to find similar items.")
st.divider()

# ─── Image upload ───────────────────────────────────────────────
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
        with st.spinner("Analysing image with Gemini..."):
            try:
                # Step 1: Extract attributes from image
                mime_type = "image/jpeg"
                if uploaded_file.name.endswith(".png"):
                    mime_type = "image/png"
                elif uploaded_file.name.endswith(".webp"):
                    mime_type = "image/webp"

                attributes = extract_attributes(image_bytes, mime_type=mime_type)
                st.success("Image analysed!")

                # Show what Gemini found
                st.subheader("📋 Detected Attributes")
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

                # Step 2: Find similar products
                st.subheader("🛍️ Similar Products Found")
                similar = find_similar_products(attributes, index, top_k=5)

                # Display results in a grid
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