import streamlit as st
import zipfile
from PIL import Image
import io

# Page Config
st.set_page_config(page_title="PicShrink Pro", page_icon="🖼️", layout="centered")

st.title("🖼️ PicShrink Pro: Compress & Ultimate BG Editor")
st.write("Upload your images, remove backgrounds, select custom sizes, and set beautiful backgrounds instantly!")

# File Uploader
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.subheader("⚙️ Processing Settings")
    
    # 1. Size Selection Options
    st.markdown("#### 📏 Size Selection")
    resize_option = st.radio("Choose Resize Method:", ["Original Size", "Custom Size (Pixels)"])
    
    custom_width = 800
    custom_height = 600
    if resize_option == "Custom Size (Pixels)":
        col1, col2 = st.columns(2)
        with col1:
            custom_width = st.number_input("Width (Pixels)", min_value=10, max_value=5000, value=800)
        with col2:
            custom_height = st.number_input("Height (Pixels)", min_value=10, max_value=5000, value=600)

    # 2. Background Options
    st.markdown("#### 🎨 Background Options")
    remove_bg = st.checkbox("🔄 Activate Background Removal (AI)")
    
    bg_mode = "Transparent"
    bg_color = "#FFFFFF"
    custom_bg_file = None
    
    if remove_bg:
        bg_mode = st.radio("Select New Background Style:", ["Transparent", "Solid Color", "Custom Background Image"])
        
        if bg_mode == "Solid Color":
            bg_color = st.color_picker("🖌️ Choose Background Color", "#FFFFFF")
        elif bg_mode == "Custom Background Image":
            custom_bg_file = st.file_uploader("📤 Upload Background Image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="bg_img_upload")

    # 3. Compression Settings
    st.markdown("#### 📉 Compression Settings")
    quality = st.slider("Compression Quality (Lower = Smaller file size)", 10, 100, 80)
    
    processed_images = []
    
    # Process Images Button
    if st.button("🚀 Process Images"):
        with st.spinner("Processing images... Please wait..."):
            
            # Load library dynamically inside the loop to avoid server freeze
            if remove_bg:
                from rembg import remove
            
            for uploaded_file in uploaded_files:
                # Read image
                img = Image.open(uploaded_file)
                
                # Step 1: Remove Background if selected
                if remove_bg:
                    img = remove(img)  # Returns an RGBA image with transparency
                    
                    # Apply solid color background if selected
                    if bg_mode == "Solid Color":
                        # Create a solid color background image matching the current image size
                        bg_img = Image.new("RGBA", img.size, bg_color)
                        bg_img.paste(img, (0, 0), img)
                        img = bg_img
                        
                    # Apply custom background image if uploaded
                    elif bg_mode == "Custom Background Image" and custom_bg_file is not None:
                        custom_bg = Image.open(custom_bg_file).convert("RGBA")
                        # Resize custom background to match the main image size
                        custom_bg = custom_bg.resize(img.size, Image.Resampling.LANCZOS)
                        custom_bg.paste(img, (0, 0), img)
                        img = custom_bg
                
                # Step 2: Custom Size Selection
                if resize_option == "Custom Size (Pixels)":
                    img = img.resize((custom_width, custom_height), Image.Resampling.LANCZOS)
                
                # Step 3: Handle Transparency Modes and Formats
                img_io = io.BytesIO()
                
                # If background is transparent, save as PNG to keep it transparent
                if remove_bg and bg_mode == "Transparent":
                    img.save(img_io, format="PNG")
                    ext = ".png"
                    mime_type = "image/png"
                else:
                    # Save as JPEG for best compression if there is a background color or original image
                    if img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGB')
                    img.save(img_io, format="JPEG", quality=quality)
                    ext = ".jpg"
                    mime_type = "image/jpeg"
                    
                img_io.seek(0)
                
                processed_images.append({
                    "name": uploaded_file.name.split('.')[0] + "_processed" + ext,
                    "data": img_io,
                    "mime": mime_type
                })
                
        st.success("🎉 All images processed successfully!")
        
        # Download Section
        if len(processed_images) == 1:
            file = processed_images[0]
            st.download_button(
                label="📥 Download Processed Image",
                data=file["data"],
                file_name=file["name"],
                mime=file["mime"]
            )
        elif len(processed_images) > 1:
            zip_io = io.BytesIO()
            with zipfile.ZipFile(zip_io, 'w') as zip_file:
                for file in processed_images:
                    zip_file.writestr(file["name"], file["data"].getvalue())
            
            zip_io.seek(0)
            st.download_button(
                label="📥 Download All as ZIP",
                data=zip_io,
                file_name="processed_images.zip",
                mime="application/zip"
            )
