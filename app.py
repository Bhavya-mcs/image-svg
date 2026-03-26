import streamlit as st
import vtracer
from rembg import remove
from PIL import Image
import io

st.title("CNC Pattern Extractor")
st.write("Turn photos of doors/panels into clean SVG vectors.")

uploaded_file = st.file_uploader("Upload Door Photo", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Load image
    input_image = Image.open(uploaded_file)
    st.image(input_image, caption="1. Original Photo", width=300)

    # Step 1: Remove Background (Isolate the pattern)
    if st.button("Extract Pattern"):
        with st.spinner("Cleaning image..."):
            # Remove the wood/background
            output_image = remove(input_image)
            
            # Convert to Grayscale to help the vectorizer
            bw_image = output_image.convert("L")
            bw_image.save("temp_cleaned.png")
            
            # Step 2: Vectorize
            vtracer.convert_image_to_svg("temp_cleaned.png", "pattern.svg", 
                                        mode="filter", 
                                        iteration=2)
            
            st.success("Pattern Extracted!")
            
            # Show Results
            col1, col2 = st.columns(2)
            with col1:
                st.image(output_image, caption="2. Cleaned Silhouette")
            with col2:
                # Preview SVG
                st.image("pattern.svg", caption="3. Final Vector Path")

            # Step 3: Download
            with open("pattern.svg", "rb") as f:
                st.download_button(
                    label="Download SVG for ArtCam/Corel",
                    data=f,
                    file_name="cnc_pattern.svg",
                    mime="image/svg+xml"
                )
