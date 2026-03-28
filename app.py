import streamlit as st
import subprocess
import tempfile
import cv2
import numpy as np
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Advanced Adaptive Lighting Engine (Handles shadows and glowing lights!)")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

st.write("### 🎛️ Advanced Scanner Settings")
col1, col2 = st.columns(2)
with col1:
    # Block size determines the "neighborhood" size the math looks at. Must be an odd number.
    block_size = st.slider("Lighting Area (Block Size)", min_value=3, max_value=199, value=45, step=2,
                           help="Increase this if the text looks too 'hollow' or fragmented.")
    # C-value fine-tunes the background noise.
    c_value = st.slider("Background Cleanliness (C-Value)", min_value=-20, max_value=40, value=10,
                        help="Higher numbers make the background whiter. Lower numbers pick up more detail.")
    
    invert = st.toggle("Invert Colors (Negative)", value=False)

with col2:
    corner_smoothing = st.slider("Corner Smoothing", min_value=0.0, max_value=1.34, value=0.2, step=0.1)
    curve_opt = st.slider("Curve Strictness", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

if uploaded_file is not None:
    # 1. Read image with OpenCV
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img_array = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    
    # 2. Add a tiny blur to remove camera static/noise
    blurred_img = cv2.GaussianBlur(img_array, (5, 5), 0)
    
    # 3. The Magic: Adaptive Thresholding
    # This adapts to the glowing light in the middle AND the shadows on the edges
    binary_img = cv2.adaptiveThreshold(
        blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, block_size, c_value
    )
    
    # CNC tools often need the negative (black cuts, white stays)
    if invert:
        binary_img = cv2.bitwise_not(binary_img)
        
    # Convert back to an image format the website can display
    bw_image = Image.fromarray(binary_img)
    
    st.write("### Live Black & White Preview")
    st.image(bw_image, use_container_width=True)

    if st.button("Generate Precision Vector"):
        with st.spinner("Calculating perfect curves..."):
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as bmp_file:
                bw_image.save(bmp_file.name, format="BMP")
                input_bmp = bmp_file.name
                
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
                output_svg = svg_file.name
                
            try:
                # 4. Run the Potrace Engine to make it smooth
                subprocess.run([
                    "potrace", input_bmp, "-s", "-a", str(corner_smoothing), 
                    "-O", str(curve_opt), "-o", output_svg
                ], check=True)
                
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("Precision curves generated!")
                st.download_button("⬇️ Download CNC SVG", svg_data, "advanced_cnc.svg", "image/svg+xml")
            except Exception as e:
                st.error("Engine Error.")
                st.write(e)
