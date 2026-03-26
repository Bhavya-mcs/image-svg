import streamlit as st
import subprocess
import tempfile
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Powered by the Potrace Engine (Same math as Inkscape/CorelDraw)")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# A simple slider to decide how dark the lines need to be before they are traced
threshold = st.slider("Darkness Threshold", min_value=10, max_value=250, value=128, 
                      help="Slide left or right until the preview below looks like a clean black and white stamp.")

if uploaded_file is not None:
    # 1. Open the image and convert to Grayscale
    image = Image.open(uploaded_file).convert('L')
    
    # 2. Force it into pure Black and White based on your slider
    # (Potrace requires a pure black and white image to trace)
    bw_image = image.point(lambda p: 255 if p > threshold else 0)
    
    st.write("### Live Black & White Preview")
    st.write("What is black will become a solid shape. What is white will be empty space.")
    st.image(bw_image, use_container_width=True)

    if st.button("Generate Smooth Vector"):
        with st.spinner("Calculating perfect curves..."):
            
            # 3. Save as a temporary BMP file (The format Potrace requires)
            with tempfile.NamedTemporaryFile(suffix=".bmp", delete=False) as bmp_file:
                bw_image.save(bmp_file.name, format="BMP")
                input_bmp = bmp_file.name
                
            # Create a temporary name for the output SVG
            with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as svg_file:
                output_svg = svg_file.name
                
            # 4. Run the Potrace Engine! 
            # -s tells it to make an SVG. -o tells it where to save it.
            try:
                subprocess.run(["potrace", input_bmp, "-s", "-o", output_svg], check=True)
                
                # Read the finished SVG
                with open(output_svg, "rb") as f:
                    svg_data = f.read()
                    
                st.success("Flawless curves generated!")
                st.download_button(
                    label="⬇️ Download CNC SVG",
                    data=svg_data,
                    file_name="perfect_cnc_vector.svg",
                    mime="image/svg+xml"
                )
            except Exception as e:
                st.error("Something went wrong with the tracing engine.")
                st.write(e)
