# Server Reset Trigger
import streamlit as st
import os
import zipfile
from PIL import Image
import io
from rembg import remove

# Page Config
st.set_page_config(page_title="PicShrink AI", page_icon="🖼️", layout="centered")

st.title("🖼️ PicShrink AI")
st.caption("AI-Powered Background Changer, Bulk ZIP & Single Image Processor")
st.divider()

# Sidebar Layout
st.sidebar.header("⚙️ Settings Panel")

# 1. Dimensions Logic
change_dim = st.sidebar.checkbox("📐 Resize Image Dimensions?", value=False)
if change_dim:
    width = st.sidebar.number_input("Width (Pixels)", value=600, step=50)
    height = st.sidebar.number_input("Height (Pixels)", value=800, step=50)

st.sidebar.divider()

# 2. AI Background Customization Logic
st.sidebar.write("🤖 **AI Background Options:**")
bg_action = st.sidebar.radio(
    "Choose Action:",
    ["Keep Original Background", "Remove Background (Transparent)", "Solid Color Background", "Custom Background Image 🖼️"]
)

selected_color = None
bg_image_file = None

if bg_action == "Solid Color Background":
    bg_color_choice = st.sidebar.selectbox("Choose Background Color", ["White", "Green", "Blue", "Black", "Red"])
    color_map = {"White": (255, 255, 255), "Green": (0, 255, 0), "Blue": (0, 0, 255), "Black": (0, 0, 0), "Red": (255, 0, 0)}
    selected_color = color_map[bg_color_choice]

elif bg_action == "Custom Background Image 🖼️":
    st.sidebar.info("📸 Upload your background image below:")
    bg_image_file = st.sidebar.file_uploader("Upload Background", type=["jpg", "jpeg", "png"])

st.sidebar.divider()

# 3. Compression Logic
apply_comp = st.sidebar.checkbox("📉 Strict File Size Limit (KB)?", value=True)
if apply_comp:
    max_kb = st.sidebar.number_input("Maximum Size (KB)", value=20, step=5)

# Main Screen File Uploader (Accepts both ZIP and Normal Images)
uploaded_file = st.file_uploader("📂 Apni photos wali ZIP file ya single photo yahan upload karein", type=["zip", "jpg", "jpeg", "png", "bmp"])

# Helper function to process a single image object
def process_single_image(img, file_name):
    # A. AI Background Action
    if bg_action == "Remove Background (Transparent)":
        processed_img = remove(img)
        ext = "png"
    elif bg_action == "Solid Color Background":
        no_bg_img = remove(img)
        background = Image.new("RGBA", no_bg_img.size, selected_color + (255,))
        processed_img = Image.alpha_composite(background, no_bg_img.convert("RGBA"))
        ext = "jpg"
    elif bg_action == "Custom Background Image 🖼️" and custom_bg is not None:
        no_bg_img = remove(img)
        resized_bg = custom_bg.resize(no_bg_img.size, Image.Resampling.LANCZOS)
        processed_img = Image.alpha_composite(resized_bg, no_bg_img.convert("RGBA"))
        ext = "jpg"
    else:
        processed_img = img.convert("RGB")
        ext = "jpg"
        
    # B. Resize Logic
    if change_dim:
        processed_img = processed_img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
        
    # C. Size Compression Logic
    img_byte_arr = io.BytesIO()
    save_format = "PNG" if ext == "png" else "JPEG"
    
    if apply_comp:
        img_quality = 95
        while img_quality > 10:
            img_byte_arr = io.BytesIO()
            if save_format == "JPEG":
                processed_img.convert("RGB").save(img_byte_arr, format=save_format, quality=img_quality)
            else:
                processed_img.save(img_byte_arr, format=save_format, optimize=True)
                break
                
            if img_byte_arr.tell() <= (max_kb * 1024):
                break
            img_quality -= 5
    else:
        if save_format == "JPEG":
            processed_img.convert("RGB").save(img_byte_arr, format=save_format, quality=85)
        else:
            processed_img.save(img_byte_arr, format=save_format)
            
    return img_byte_arr.getvalue(), ext

if uploaded_file is not None:
    st.success("File loaded successfully!")
    
    # Validation for Custom Background
    if bg_action == "Custom Background Image 🖼️" and bg_image_file is None:
        st.warning("⚠️ Please upload a custom background image from the sidebar first!")
    else:
        if st.button("🚀 Process Images"):
            with st.spinner("AI is working... Processing your request..."):
                
                # Load custom background if available
                custom_bg = None
                if bg_action == "Custom Background Image 🖼️" and bg_image_file is not None:
                    custom_bg = Image.open(bg_image_file).convert("RGBA")
                
                is_zip = uploaded_file.name.lower().endswith('.zip')
                
                if is_zip:
                    # ---- ZIP FILE PROCESSING ----
                    input_zip = zipfile.ZipFile(uploaded_file)
                    output_buffer = io.BytesIO()
                    count = 0
                    
                    with zipfile.ZipFile(output_buffer, "w", zipfile.ZIP_DEFLATED) as out_zip:
                        for file_name in input_zip.namelist():
                            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) and not file_name.startswith('__MACOSX'):
                                try:
                                    img_data = input_zip.read(file_name)
                                    img = Image.open(io.BytesIO(img_data))
                                    
                                    file_bytes, final_ext = process_single_image(img, file_name)
                                    
                                    base_name = os.path.basename(file_name)
                                    name_without_ext = os.path.splitext(base_name)[0]
                                    
                                    if name_without_ext:
                                        out_zip.writestr(f"{name_without_ext}.{final_ext}", file_bytes)
                                        count += 1
                                except:
                                    pass
                    
                    if count > 0:
                        st.balloons()
                        st.success(f"Mubarak ho Hafiz! Tamam {count} photos ready hain.")
                        st.download_button(
                            label="📥 Apni ready ZIP file yahan se download karein",
                            data=output_buffer.getvalue(),
                            file_name="PicShrink_Master_Output.zip",
                            mime="application/zip"
                        )
                else:
                    # ---- SINGLE IMAGE PROCESSING ----
                    try:
                        img = Image.open(uploaded_file)
                        file_bytes, final_ext = process_single_image(img, uploaded_file.name)
                        
                        name_without_ext = os.path.splitext(uploaded_file.name)[0]
                        
                        st.balloons()
                        st.success("Mubarak ho Hafiz! Aap ki photo AI se process ho chuki hai.")
                        st.download_button(
                            label="📥 Apni ready photo yahan se download karein",
                            data=file_bytes,
                            file_name=f"{name_without_ext}_processed.{final_ext}",
                            mime=f"image/{final_ext}"
                        )
                    except Exception as e:
                        st.error(f"Image process karne mein koi masla aaya: {e}")
