import streamlit as st
import subprocess
import tempfile
import cv2
import numpy as np
from PIL import Image
import os

st.set_page_config(page_title="Ultimate CNC Vector", layout="wide")

st.title("🖼️ Ultimate CNC Vector Extractor")
st.write("Master control panel: Every setting unlocked.")

# --- THE MASTER SIDEBAR ---
st.sidebar.title("🎛️ Master Controls")

st.sidebar.write("### ✂️ Step 1: Crop")
crop_top = st.sidebar.slider("Crop Top (%)", 0, 40, 0)
crop_bottom = st.sidebar.slider("Crop Bottom (%)", 0, 40, 0)
crop_left = st.sidebar.slider("Crop Left (%)", 0, 40, 0)
crop_right = st.sidebar.slider("Crop Right (%)", 0, 40, 0)

st.sidebar.write("---")
st.sidebar.write("### 💧 Step 2: Pre-Processing")
blur_amount = st.sidebar.slider("Pre-Blur (Wood Grain remover)", min_value=1, max_value=31, value=5, step=2)

st.sidebar.write("---")
st.sidebar.write("### 💡 Step 3: Lighting Engine")
lighting_mode = st.sidebar.radio("Choose Lighting Math:", ["Basic (Darkness Slider)", "Advanced (Adaptive Scanner)"])

if lighting_mode == "Basic (Darkness Slider)":
    threshold_val = st.sidebar.slider("Darkness Threshold", 10, 250, 128)
else:
    block_size = st.sidebar.slider("Lighting Area (Block Size)", 3, 199, 45, step=2)
    c_value = st.sidebar.slider("Background Cleanliness", -20, 40, 10)

invert = st.sidebar.toggle("Invert Colors (Negative)", value=False)

st.sidebar.write("---")
st.sidebar.write("### 📐 Step 4: Potrace Math")
dust_size = st.sidebar.slider("Ignore Dust (Despeckle)", 0, 50, 2)
corner_smoothing = st.sidebar.slider("Corner Smoothing", 0.0, 1.34, 0.2, step=0.1)
curve_opt = st.sidebar.slider("Curve Strictness", 0.0, 1.0, 0.0, step=0.1)


# --- MAIN SCREEN ---
uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 1. Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    original_img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
    h, w = original_img.shape
    
    # 2. Crop
    top_px = int(h * (crop_top / 100))
    bottom_px = int(h * (1 - (crop_bottom / 100)))
    left_px = int(w * (crop_left / 100))
    right_px = int(w * (1 - (crop_right / 100)))
    cropped_img = original_img[top_px:bottom_px, left_px:right_px]
    
    # 3. Blur (Noise Reduction)
    blurred_img = cv2.GaussianBlur(cropped_img, (blur_amount, blur_amount), 0)
    
    # 4. Lighting Threshold
    if lighting_mode == "Basic (Darkness Slider)":
        _, binary_img = cv2.threshold(blurred_img, threshold_val, 255, cv2.THRESH_BINARY)
    else:
        binary_img = cv2.adaptiveThreshold(
            blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, block_size, c_value
        )
    
    # 5. Invert if needed
    if invert:
        binary_img = cv2.bitwise_not(binary_img)
        
    bw_image = Image.fromarray(binary_img)
    
    st.write("### Live Black & White Preview")
    st.write("What is **Black** will be cut by the CNC. What is **White** is empty space.")
    st.image(bw_image, use_container_width=True)

    if st.button("Generate Ultimate Vector", use_container_width=True):
        with st.spinner("Calculating perfect curves..."):
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as bmp_file:
                bw_image.save(bmp_file.name, format="BMP")
                input_bmp = bmp_file.name
                
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
                output_svg = svg_file.name
                
            try:
                # 6. Run Potrace with ALL settings
                subprocess.run([
                    "potrace", input_bmp, "-s", 
                    "-a", str(corner_smoothing), 
                    "-O", str(curve_opt), 
                    "-t", str(dust_size), 
                    "-o", output_svg
                ], check=True)
                
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("Vector generated successfully!")
                st.download_button("⬇️ Download CNC SVG", svg_data, "ultimate_cnc_vector.svg", "image/svg+xml", use_container_width=True)
            except Exception as e:
                st.error("Engine Error.")
                st.write(e)
