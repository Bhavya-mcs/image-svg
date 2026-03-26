import streamlit as st
import vtracer
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Image to SVG Vector")
st.write("Ready to trace!")

uploaded_file = st.file_uploader("Upload your image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 1. Get the exact "GPS" paths for the cloud server
    input_path = os.path.abspath("input.png")
    output_path = os.path.abspath("output.svg")

    # 2. Save the file using that exact path
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.image(input_path, caption="Uploaded Image", width=300)

    if st.button("Convert to Vector"):
        with st.spinner("Tracing..."):
            # 3. Give vtracer the exact paths
            vtracer.convert_image_to_svg_py(input_path, output_path)
            
            st.success("Conversion Complete!")
            st.image(output_path, caption="Vector Preview")
            
            with open(output_path, "rb") as f:
                st.download_button("Download SVG File", f, "cnc_design.svg")
