import streamlit as st
import vtracer
from PIL import Image
import os

st.set_page_config(page_title="CNC Vector Creator")

st.title("🖼️ Image to SVG Vector")
st.write("If you see this, the app is working!")

uploaded_file = st.file_uploader("Upload your image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Save temp file
    with open("input.png", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.image("input.png", caption="Uploaded Image", width=300)

    if st.button("Convert to Vector"):
        with st.spinner("Tracing..."):
            # This is the most stable version of the command
            vtracer.convert_image_to_svg(
                input_path="input.png", 
                output_path="output.svg"
            )
            
            st.success("Done!")
            # Note: We use st.image to show the SVG preview
            st.image("output.svg", caption="Vector Preview")
            
            with open("output.svg", "rb") as f:
                st.download_button("Download SVG", f, "result.svg")
