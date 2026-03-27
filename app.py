import streamlit as st
import subprocess
import tempfile
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Powered by the Potrace Engine (Same math as Inkscape/CorelDraw)")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# --- ADVANCED POTRACE CONTROLS ---
st.write("### 🎛️ Trace Settings")
col1, col2 = st.columns(2)
with col1:
    threshold = st.slider("Darkness Threshold", min_value=10, max_value=250, value=128)
    
    # t controls ignoring tiny specks of dust (Despeckle)
    dust_size = st.slider("Ignore Dust (Despeckle)", min_value=0, max_value=50, value=2, 
                          help="Removes tiny black specks. Increase if your image has wood grain noise.")

with col2:
    # alphamax controls corner rounding. 0 = sharp, 1.34 = max smooth.
    corner_smoothing = st.slider("Corner Smoothing", min_value=0.0, max_value=1.34, value=0.2, step=0.1, 
                                 help="0.0 = Razor sharp corners. 1.3 = Highly rounded/smooth corners.")
    
    # opttolerance controls how closely the curve follows the original pixels
    curve_opt = st.slider("Curve Strictness", min_value=0.0, max_value=1.0, value=0.0, step=0.1, 
                          help="0.0 = Follows your shape strictly. Higher = Looser, more 'melted' curves.")


if uploaded_file is not None:
    # 1. Open the image and convert to Grayscale
    image = Image.open(uploaded_file).convert('L')
    
    # 2. Force it into pure Black and White
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
                # 3. Run the Potrace Engine with our custom slider values!
                subprocess.run([
                    "potrace", input_bmp, 
                    "-s", # Output as SVG
                    "-a", str(corner_smoothing), # Corner Sharpness
                    "-O", str(curve_opt),        # Curve Optimization
                    "-t", str(dust_size),        # Dust/Noise removal
                    "-o", output_svg
                ], check=True)
                
                # Read the finished SVG
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("Precision curves generated!")
                st.download_button(
                    label="⬇️ Download CNC SVG",
                    data=svg_data,
                    file_name="precision_cnc_vector.svg",
                    mime="image/svg+xml"
                )
            except Exception as e:
                st.error("Something went wrong with the tracing engine.")
                st.write(e)
