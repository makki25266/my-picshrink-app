
import streamlit as st
import zipfile
from PIL import Image
import io

# Page Config
st.set_page_config(page_title="PicShrink Pro", page_icon="🖼️", layout="centered")

st.title("🖼️ PicShrink Pro: Target KB Compressor & BG Editor")
st.write("Upload your images, set your exact desired KB size, and let the AI handle the rest!")

# File Uploader
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.subheader("⚙️ Processing Settings")
    
    # 1. Size Selection Options
    st.markdown("#### 📏 Size Selection")
    resize_option = st.radio("Choose Resize Method:", ["Original Dimensions", "Custom Dimensions (Pixels)"])
    
    custom_width = 800
    custom_height = 600
    if resize_option == "Custom Dimensions (Pixels)":
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

    # 3. Smart KB Compression Settings
    st.markdown("#### 📉 Target File Size (KB)")
    target_kb = st.number_input("Enter Maximum File Size (KB) you want:", min_value=5, max_value=10000, value=50, step=5)
    
    processed_images = []
    
    # Process Images Button
    if st.button("🚀 Process Images"):
        with st.spinner("Processing images to match your target KB... Please wait..."):
            
            # Load library dynamically inside the loop to avoid server freeze
            if remove_bg:
                from rembg import remove
            
            st.markdown("### 📊 Compression Results:")
            
            for uploaded_file in uploaded_files:
                # Calculate Original Size in KB
                uploaded_file.seek(0, io.SEEK_END)
                orig_size_kb = uploaded_file.tell() / 1024
                uploaded_file.seek(0)
                
                # Read image
                img = Image.open(uploaded_file)
                
                # Step 1: Remove Background if selected
                if remove_bg:
                    img = remove(img)
                    
                    if bg_mode == "Solid Color":
                        bg_img = Image.new("RGBA", img.size, bg_color)
                        bg_img.paste(img, (0, 0), img)
                        img = bg_img
                        
                    elif bg_mode == "Custom Background Image" and custom_bg_file is not None:
                        custom_bg = Image.open(custom_bg_file).convert("RGBA")
                        custom_bg = custom_bg.resize(img.size, Image.Resampling.LANCZOS)
                        custom_bg.paste(img, (0, 0), img)
                        img = custom_bg
                
                # Step 2: Custom Dimensions
                if resize_option == "Custom Dimensions (Pixels)":
                    img = img.resize((custom_width, custom_height), Image.Resampling.LANCZOS)
                
                # Step 3: Smart Loop to hit the exact Target KB
                ext = ".png" if (remove_bg and bg_mode == "Transparent") else ".jpg"
                mime_type = "image/png" if ext == ".png" else "image/jpeg"
                
                # If PNG (Transparent), standard compression is limited, so we save directly
                if ext == ".png":
                    img_io = io.BytesIO()
                    img.save(img_io, format="PNG")
                    new_size_kb = len(img_io.getvalue()) / 1024
                else:
                    # For JPEG, we look for the best quality that fits the target KB
                    if img.mode in ('RGBA', 'LA'):
                        img = img.convert('RGB')
                        
                    q = 95  # Start with high quality
                    while q > 5:
                        img_io = io.BytesIO()
                        img.save(img_io, format="JPEG", quality=q)
                        new_size_kb = len(img_io.getvalue()) / 1024
                        
                        # If size is under target, we stop!
                        if new_size_kb <= target_kb:
                            break
                        q -= 5  # Reduce quality step by step to shrink size
                
                img_io.seek(0)
                
                # Display results
                if new_size_kb > target_kb and ext == ".png":
                    st.warning(f"⚠️ **{uploaded_file.name}**: PNG transparency format cannot compress below `{target_kb} KB`. Best achieved: `{new_size_kb:.2f} KB`.")
                else:
                    st.info(f"📄 **{uploaded_file.name}**:\n* Original Size: `{orig_size_kb:.2f} KB` \n* New Compressed Size: `{new_size_kb:.2f} KB` (Quality Level: {q if ext=='.jpg' else 'PNG'})")
                
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
