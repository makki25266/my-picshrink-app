import streamlit as st
import os
import zipfile
from PIL import Image
import io

# Simple Page Title
st.set_page_config(page_title="PicShrink AI", page_icon="🖼️", layout="centered")

st.title("🖼️ PicShrink AI")
st.write("Bulk Image Resizer, Background Changer & Compressor")
st.divider()

# Sidebar Layout
st.sidebar.header("⚙️ Settings Panel")

change_dim = st.sidebar.checkbox("📐 Resize Image Dimensions?", value=True)
if change_dim:
    width = st.sidebar.number_input("Width (Pixels)", value=600, step=50)
    height = st.sidebar.number_input("Height (Pixels)", value=800, step=50)

change_bg = st.sidebar.checkbox("🎨 Change Background Color?", value=False)
if change_bg:
    bg_color_choice = st.sidebar.selectbox("Choose Background Color", ["White", "Green", "Blue", "Black", "Red"])
    color_map = {"White": "#FFFFFF", "Green": "#00FF00", "Blue": "#0000FF", "Black": "#000000", "Red": "#FF0000"}
    selected_color = color_map[bg_color_choice]

apply_comp = st.sidebar.checkbox("📉 Strict File Size Limit (KB)?", value=True)
if apply_comp:
    max_kb = st.sidebar.number_input("Maximum Size (KB)", value=20, step=5)

# Main Screen File Uploader
uploaded_file = st.file_uploader("📂 Apni photos wali ZIP file yahan upload karein", type=["zip"])

if uploaded_file is not None:
    st.success("ZIP File loaded successfully!")
    
    if st.button("🚀 Process Images"):
        with st.spinner("Processing... Please wait..."):
            input_zip = zipfile.ZipFile(uploaded_file)
            output_buffer = io.BytesIO()
            count = 0
            
            with zipfile.ZipFile(output_buffer, "w", zipfile.ZIP_DEFLATED) as out_zip:
                for file_name in input_zip.namelist():
                    if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')) and not file_name.startswith('__MACOSX'):
                        try:
                            img_data = input_zip.read(file_name)
                            img = Image.open(io.BytesIO(img_data))
                            
                            # 1. Background Logic
                            if change_bg:
                                img = img.convert("RGBA")
                                bg_layer = Image.new("RGBA", img.size, selected_color)
                                current_img = Image.alpha_composite(bg_layer, img).convert("RGB")
                            else:
                                current_img = img.convert("RGB")
                                
                            # 2. Resize Logic
                            if change_dim:
                                current_img = current_img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                                
                            # 3. Size Compression Logic
                            img_byte_arr = io.BytesIO()
                            if apply_comp:
                                img_quality = 95
                                while img_quality > 10:
                                    img_byte_arr = io.BytesIO()
                                    current_img.save(img_byte_arr, format="JPEG", quality=img_quality)
                                    if img_byte_arr.tell() <= (max_kb * 1024):
                                        break
                                    img_quality -= 5
                            else:
                                current_img.save(img_byte_arr, format="JPEG", quality=85)
                            
                            # 4. Strict Extension Fix (.jpg append)
                            base_name = os.path.basename(file_name)
                            name_without_ext = os.path.splitext(base_name)[0]
                            
                            if name_without_ext:
                                out_zip.writestr(f"{name_without_ext}.jpg", img_byte_arr.getvalue())
                                count += 1
                        except:
                            pass

            if count > 0:
                st.balloons()
                st.success(f"Mubarak ho! Tamam {count} photos ready hain.")
                
                st.download_button(
                    label="📥 Apni ready ZIP file yahan se download karein",
                    data=output_buffer.getvalue(),
                    file_name="PicShrink_Output.zip",
                    mime="application/zip"
                )