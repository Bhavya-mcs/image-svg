import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Adjust the slider until your pattern looks perfectly crisp!")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# The slider controls the light/dark balance
threshold = st.slider("Vector Detail (Threshold)", min_value=0, max_value=255, value=128)

if uploaded_file is not None:
    # Read the image and make it Grayscale
    image = Image.open(uploaded_file).convert('L')
    img_array = np.array(image)
    
    # Create the Black & White mask based on the slider
    _, binary_img = cv2.threshold(img_array, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # LIVE PREVIEW: This is the magic addition!
    st.write("### 1. Live CNC Mask Preview")
    st.write("The white areas are what will be traced into vector lines.")
    st.image(binary_img, use_container_width=True)

    if st.button("Generate Clean Vector"):
        with st.spinner("Calculating paths..."):
            
            # Find all the edges (RETR_LIST ensures we get inside cuts too)
            contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                st.error("No pattern found! Try moving the slider.")
            else:
                # Build the SVG file as text
                h, w = img_array.shape
                svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                svg_content += f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
                
                for contour in contours:
                    # Ignore tiny specks of dust (less than 3 points)
                    if len(contour) > 2:
                        path_str = "M " + " L ".join([f"{pt[0][0]},{pt[0][1]}" for pt in contour]) + " Z"
                        # Use 'stroke' instead of 'fill' so it creates wireframe paths
                        svg_content += f'<path d="{path_str}" fill="none" stroke="black" stroke-width="1.5" />\n'
                        
                svg_content += '</svg>'
                
                st.success(f"Vector Generated! Found {len(contours)} cut paths.")
                
                # Directly offer the text as a file download (cleaner than tempfiles)
                st.download_button(
                    label="⬇️ Download SVG Outline for ArtCam",
                    data=svg_content.encode("utf-8"),
                    file_name="cnc_paths.svg",
                    mime="image/svg+xml"
                )
