import streamlit as st
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Using OpenCV for 100% crash-proof vector tracing.")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# Add a slider so you can control how dark the trace is!
threshold = st.slider("Vector Detail (Threshold)", min_value=50, max_value=255, value=128, 
                      help="Lower = captures more dark areas. Higher = captures less.")

if uploaded_file is not None:
    # 1. Read the image safely
    image = Image.open(uploaded_file).convert('L') # Convert to Grayscale
    img_array = np.array(image)
    
    st.image(image, caption="Original Image", width=300)

    if st.button("Generate Clean Vector"):
        with st.spinner("Calculating paths..."):
            
            # 2. Turn image into pure black and white based on your slider
            _, binary_img = cv2.threshold(img_array, threshold, 255, cv2.THRESH_BINARY_INV)
            
            # 3. Find the exact edges (Paths for CNC)
            contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 4. Draw the SVG mathematically
            h, w = img_array.shape
            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
            
            for contour in contours:
                # Ignore tiny dust particles (less than 5 points)
                if len(contour) > 5:
                    # Convert coordinates to an SVG path
                    path_str = "M " + " L ".join([f"{pt[0][0]},{pt[0][1]}" for pt in contour]) + " Z"
                    svg_content += f'<path d="{path_str}" fill="black" stroke="none" />\n'
                    
            svg_content += '</svg>'
            
            # 5. Save and Download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_out:
                temp_out.write(svg_content.encode("utf-8"))
                output_path = temp_out.name
                
            st.success("Vector Generated Successfully!")
            
            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download SVG for ArtCam", f, "cnc_contour.svg")
