import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Pro CNC Vector Extractor")
st.write("Create solid, smooth, and clean vectors for your CNC!")

uploaded_file = st.file_uploader("Upload your photo or design", type=["jpg", "png", "jpeg"])

# --- THE UPGRADED CONTROL PANEL ---
col1, col2, col3 = st.columns(3)
with col1:
    threshold = st.slider("Darkness", min_value=0, max_value=255, value=128)
with col2:
    blur_amount = st.slider("Blur Noise", min_value=1, max_value=21, value=3, step=2)
with col3:
    # This new slider controls the mathematical smoothing of the curves!
    smoothness = st.slider("Line Smoothness", min_value=0.0, max_value=3.0, value=1.0, step=0.1)

if uploaded_file is not None:
    # Read the image and make it Grayscale
    image = Image.open(uploaded_file).convert('L')
    img_array = np.array(image)
    
    blurred_img = cv2.GaussianBlur(img_array, (blur_amount, blur_amount), 0)
    _, binary_img = cv2.threshold(blurred_img, threshold, 255, cv2.THRESH_BINARY_INV)
    
    st.write("### Live Mask Preview")
    st.image(binary_img, use_container_width=True)

    if st.button("Generate Clean Vector"):
        with st.spinner("Calculating smooth paths..."):
            
            # RETR_TREE is smarter: it understands shapes inside of other shapes (holes)
            contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                st.error("No pattern found! Try moving the sliders.")
            else:
                h, w = img_array.shape
                svg_content = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
                svg_content += f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">\n'
                
                # We will combine all paths into one massive shape
                path_data = ""
                
                for contour in contours:
                    if len(contour) > 5:
                        # --- THE MAGIC SMOOTHER ---
                        # This removes the jagged pixels and creates sweeping curves
                        epsilon = (smoothness / 1000.0) * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) > 2:
                            path_str = "M " + " L ".join([f"{pt[0][0]},{pt[0][1]}" for pt in approx]) + " Z "
                            path_data += path_str
                            
                # The 'evenodd' rule fills the shapes but keeps the holes perfectly clear!
                svg_content += f'<path d="{path_data}" fill="black" fill-rule="evenodd" stroke="none" />\n'
                svg_content += '</svg>'
                
                st.success(f"Smooth Vector Generated! Found {len(contours)} clean shapes.")
                
                st.download_button(
                    label="⬇️ Download Clean Solid SVG",
                    data=svg_content.encode("utf-8"),
                    file_name="cnc_mandala_clean.svg",
                    mime="image/svg+xml"
                )
