import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Adjust the sliders until your pattern looks perfectly crisp and smooth!")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# --- THE CONTROL PANEL ---
col1, col2 = st.columns(2)
with col1:
    threshold = st.slider("Vector Detail (Threshold)", min_value=0, max_value=255, value=128)
with col2:
    # Blur kernel size must be an odd number, so we use step=2
    blur_amount = st.slider("Smoothness (Blur)", min_value=1, max_value=31, value=5, step=2)

if uploaded_file is not None:
    # Read the image and make it Grayscale
    image = Image.open(uploaded_file).convert('L')
    img_array = np.array(image)
    
    # --- NEW: Apply the Blur to melt away wood grain ---
    blurred_img = cv2.GaussianBlur(img_array, (blur_amount, blur_amount), 0)
    
    # Create the Black & White mask based on the BLURRED image
    _, binary_img = cv2.threshold(blurred_img, threshold, 255, cv2.THRESH_BINARY_INV)
    
    # LIVE PREVIEW
    st.write("### Live CNC Mask Preview")
    st.write("The white areas are what will be traced into vector lines.")
    st.image(binary_img, use_container_width=True)

    if st.button("Generate Clean Vector"):
        with st.spinner("Calculating smooth paths..."):
            
            # Find all the edges
            contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                st.error("No pattern found! Try moving the sliders.")
            else:
                # Build the SVG file as text
                h, w = img_array.shape
                svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                svg_content += f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
                
                for contour in contours:
                    # Filter out tiny dust particles (increased to 5 points for cleaner cuts)
                    if len(contour) > 5:
                        path_str = "M " + " L ".join([f"{pt[0][0]},{pt[0][1]}" for pt in contour]) + " Z"
                        svg_content += f'<path d="{path_str}" fill="none" stroke="black" stroke-width="1.5" />\n'
                        
                svg_content += '</svg>'
                
                st.success(f"Smooth Vector Generated! Found {len(contours)} cut paths.")
                
                st.download_button(
                    label="⬇️ Download SVG Outline for ArtCam",
                    data=svg_content.encode("utf-8"),
                    file_name="cnc_paths_smooth.svg",
                    mime="image/svg+xml"
                )
