import streamlit as st
import subprocess
import tempfile
from PIL import Image
import os
from rembg import remove

st.set_page_config(page_title="AI CNC Vector Creator")

st.title("🤖 AI-Powered CNC Vector Extractor")
st.write("Uses AI to isolate your pattern, and Potrace to draw perfect CNC curves.")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# --- AI & TRACE CONTROLS ---
st.write("### 🎛️ AI & Trace Settings")

use_ai = st.toggle("✨ Use AI to Remove Background (Recommended for Photos)", value=False, 
                   help="Turn this on if your photo has wood grain, shadows, or a messy background.")

col1, col2 = st.columns(2)
with col1:
    threshold = st.slider("Darkness Threshold", min_value=10, max_value=250, value=128)
    dust_size = st.slider("Ignore Dust (Despeckle)", min_value=0, max_value=50, value=2)

with col2:
    corner_smoothing = st.slider("Corner Smoothing", min_value=0.0, max_value=1.34, value=0.2, step=0.1)
    curve_opt = st.slider("Curve Strictness", min_value=0.0, max_value=1.0, value=0.0, step=0.1)

if uploaded_file is not None:
    # 1. Open the original image
    original_image = Image.open(uploaded_file).convert('RGBA')
    
    # 2. AI Processing Step
    if use_ai:
        with st.spinner("AI is analyzing and cleaning the image (this takes a moment)..."):
            # The AI removes the background, leaving the pattern on a transparent layer
            ai_cleaned = remove(original_image)
            
            # Create a pure white background to put the clean pattern onto
            white_bg = Image.new("RGBA", ai_cleaned.size, "WHITE")
            white_bg.paste(ai_cleaned, (0, 0), ai_cleaned)
            
            # Convert to Grayscale for Potrace
            working_image = white_bg.convert('L')
    else:
        working_image = original_image.convert('L')
    
    # 3. Force into Black and White for the CNC engine
    bw_image = working_image.point(lambda p: 255 if p > threshold else 0)
    
    st.write("### Live Black & White Preview")
    st.image(bw_image, use_container_width=True)

    if st.button("Generate AI Precision Vector"):
        with st.spinner("Calculating perfect curves..."):
            
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as bmp_file:
                bw_image.save(bmp_file.name, format="BMP")
                input_bmp = bmp_file.name
                
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
                output_svg = svg_file.name
                
            try:
                # 4. Run the Potrace Engine
                subprocess.run([
                    "potrace", input_bmp, 
                    "-s", 
                    "-a", str(corner_smoothing), 
                    "-O", str(curve_opt),        
                    "-t", str(dust_size),        
                    "-o", output_svg
                ], check=True)
                
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("AI Precision curves generated!")
                st.download_button(
                    label="⬇️ Download AI CNC SVG",
                    data=svg_data,
                    file_name="ai_precision_cnc.svg",
                    mime="image/svg+xml"
                )
            except Exception as e:
                st.error("Something went wrong with the tracing engine.")
                st.write(e)
