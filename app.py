

                 import streamlit as st
import zipfile
from PIL import Image
import io

# Page Config
st.set_page_config(page_title="PicShrink Pro", page_icon="🖼️", layout="centered")

st.title("🖼️ PicShrink Pro: Compress & Remove Background")
st.write("Upload your images, remove backgrounds, compress sizes, and download them instantly!")

# File Uploader
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Settings
    st.subheader("⚙️ Processing Settings")
    remove_bg = st.checkbox("Remove Background (AI)")
    quality = st.slider("Compression Quality (Lower = Smaller file size)", 10, 100, 80)
    
    processed_images = []
    
    # Process Images Button
    if st.button("🚀 Process Images"):
        with st.spinner("Processing images... Please wait..."):
            
            # If user wants to remove background, load the library inside the process loop
            if remove_bg:
                from rembg import remove
            
            for uploaded_file in uploaded_files:
                # Read image
                img = Image.open(uploaded_file)
                
                # Step 1: Remove Background if selected
                if remove_bg:
                    img = remove(img)
                
                # Step 2: Convert to RGB for saving as JPEG if it's not transparent anymore
                if img.mode in ('RGBA', 'LA') and not remove_bg:
                    img = img.convert('RGB')
                elif img.mode == 'RGBA' and remove_bg:
                    # Keep RGBA mode to preserve transparency after background removal
                    pass
                else:
                    img = img.convert('RGB')
                
                # Step 3: Compress image into memory
                img_io = io.BytesIO()
                if remove_bg:
                    img.save(img_io, format="PNG")  # PNG preserves transparency
                else:
                    img.save(img_io, format="JPEG", quality=quality)
                    
                img_io.seek(0)
                
                processed_images.append({
                    "name": uploaded_file.name,
                    "data": img_io
                })
                
        st.success("🎉 All images processed successfully!")
        
        # Download Section
        if len(processed_images) == 1:
            # Single file download
            file = processed_images[0]
            ext = ".png" if remove_bg else ".jpg"
            st.download_button(
                label="📥 Download Processed Image",
                data=file["data"],
                file_name=file["name"].split('.')[0] + "_processed" + ext,
                mime="image/png" if remove_bg else "image/jpeg"
            )
        elif len(processed_images) > 1:
            # ZIP download for multiple files
            zip_io = io.BytesIO()
            with zipfile.ZipFile(zip_io, 'w') as zip_file:
                for file in processed_images:
                    ext = ".png" if remove_bg else ".jpg"
                    zip_file.writestr(file["name"].split('.')[0] + "_processed" + ext, file["data"].getvalue())
            
            zip_io.seek(0)
            st.download_button(
                label="📥 Download All as ZIP",
                data=zip_io,
                file_name="processed_images.zip",
                mime="application/zip"
            )      
