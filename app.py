import streamlit as st
import subprocess
import tempfile
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Use the sliders to isolate your pattern for perfect CNC curves.")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

st.write("### 🎛️ Trace Settings")
col1, col2 = st.columns(2)
with col1:
    threshold = st.slider("Darkness Threshold", min_value=10, max_value=250, value=128)
    dust_size = st.slider("Ignore Dust (Despeckle)", min_value=0, max_value=50, value=2)

with col2:
    corner_smoothing = st.slider("Corner Smoothing", min_value=0.0, max_value=1.34, value=0.2, step=0.1)
    curve_opt = st.slider("Curve Strictness", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('L')
    bw_image = image.point(lambda p: 255 if p > threshold else 0)
    
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
                subprocess.run([
                    "potrace", input_bmp, "-s", "-a", str(corner_smoothing), 
                    "-O", str(curve_opt), "-t", str(dust_size), "-o", output_svg
                ], check=True)
                
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("Precision curves generated!")
                st.download_button("⬇️ Download CNC SVG", svg_data, "precision_cnc.svg", "image/svg+xml")
            except Exception as e:
                st.error("Engine Error.")
                st.write(e)
