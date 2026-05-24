# app.py
# This is the main web interface for the shopping agent.
# Streamlit turns this Python file into a web app automatically.
# Run it with: streamlit run app.py

import streamlit as st
from PIL import Image
import io
import sys
sys.path.append('.')
from src.vision.extractor import extract_attributes

# ─── Page config ────────────────────────────────────────────────
# This must be the first Streamlit command in the file.
# Sets the browser tab title, icon, and layout.
st.set_page_config(
    page_title="AI Shopping Agent",
    page_icon="🛍️",
    layout="centered"
)

# ─── Header ─────────────────────────────────────────────────────
st.title("🛍️ AI Shopping Agent")
st.markdown("Upload a product image and Gemini will identify what it is.")
st.divider()

# ─── Image upload ───────────────────────────────────────────────
# st.file_uploader creates a drag-and-drop upload box.
# It returns None if nothing is uploaded yet.
uploaded_file = st.file_uploader(
    "Upload a product image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supports JPG, PNG, and WebP"
)

if uploaded_file is not None:

    # Read the uploaded file into memory as bytes
    image_bytes = uploaded_file.read()

    # Show the uploaded image in the UI
    image = Image.open(io.BytesIO(image_bytes))
    st.image(image, caption="Uploaded image", use_container_width=True)

    st.divider()

    # ─── Analyse button ─────────────────────────────────────────
    # Only runs Gemini when the user clicks the button.
    # This prevents unnecessary API calls on every rerender.
    if st.button("🔍 Analyse Product", type="primary", use_container_width=True):

        # st.spinner shows a loading animation while Gemini is thinking
        with st.spinner("Gemini is analysing your image..."):
            try:
                # Determine mime type from uploaded file
                mime_type = "image/jpeg"
                if uploaded_file.name.endswith(".png"):
                    mime_type = "image/png"
                elif uploaded_file.name.endswith(".webp"):
                    mime_type = "image/webp"

                # Call extractor.py — sends image to Gemini
                attributes = extract_attributes(image_bytes, mime_type=mime_type)

                # ─── Display results ────────────────────────────
                st.success("Analysis complete!")
                st.subheader("📋 Product Attributes")

                # Display each attribute in a clean two-column grid
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

                # Also show the raw JSON for transparency
                with st.expander("🔧 Raw JSON from Gemini"):
                    st.json(attributes)

                # Store result in session state for Week 3 agent
                # Session state persists across rerenders in the same session
                st.session_state['last_attributes'] = attributes
                st.session_state['last_image'] = image_bytes

                st.info("Week 2 coming soon: find similar products from our catalogue!")

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
                st.markdown("**Common fixes:**")
                st.markdown("- Check your internet connection")
                st.markdown("- Make sure your .env file has the correct Project ID")
                st.markdown("- Check GCP Console that Vertex AI API is enabled")

else:
    # Placeholder shown before any image is uploaded
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