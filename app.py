import streamlit as st
import vtracer
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Image to SVG Vector")
st.write("Ready to trace!")

uploaded_file = st.file_uploader("Upload your image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 1. Create guaranteed-safe temporary files that the cloud server allows
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_in:
        input_path = temp_in.name
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_out:
        output_path = temp_out.name

    # 2. Open the uploaded file and force it to save as a clean PNG
    image = Image.open(uploaded_file)
    image.save(input_path, format="PNG")
    
    st.image(image, caption="Uploaded Image", width=300)

    if st.button("Convert to Vector"):
        with st.spinner("Tracing..."):
            # 3. Use the safe temp paths and set it to Black & White for CNC
            vtracer.convert_image_to_svg_py(
                input_path, 
                output_path, 
                colormode="bw"
            )
            
            st.success("Conversion Complete!")
            st.image(output_path, caption="Vector Preview")
            
            # 4. Read the safe SVG and provide the download
            with open(output_path, "rb") as f:
                st.download_button("Download SVG File", f, "cnc_design.svg")
