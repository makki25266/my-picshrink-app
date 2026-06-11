import streamlit as st
import os
import zipfile
from PIL import Image
import io

# App Layout & Design
st.set_page_config(page_title="PicShrink AI", page_icon="🖼️", layout="centered")

st.markdown("""
    <style>
    .title-text { font-family: 'Arial', sans-serif; color: #4A154B; font-weight: bold; text-align: center; }
    .subtitle-text { color: #555555; text-align: center; margin-bottom: 25px; }
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #FF416C, #FF4B2B);
        color: white; border-radius: 20px; border: none;
        padding: 12px 30px; font-size: 18px; font-weight: bold; width: 100%;
        box-shadow: 0px 4px 15px rgba(255, 65, 108, 0.3);
    }
    </style>
""", unsafe_allowed_html=True)

st.markdown("<h1 class='title-text'>🖼️ PicShrink AI</h1>", unsafe_allowed_html=True)
st.markdown("<p class='subtitle-text'>Bulk Image Resizer, Background Changer & Compressor</p>", unsafe_allowed_html=True)
st.divider()

# Sidebar Setup
st.sidebar.header("⚙️ Settings Panel")

change_dim = st.sidebar.checkbox("📐 Resize Image Dimensions?", value=True)
if change_dim:
    width = st.sidebar.number_input("Width (Pixels)", value=600, step=50)
    height = st.sidebar.number_input("Height (Pixels)", value=800, step=50)

change_bg = st.sidebar.checkbox("🎨 Change Background Color?", value=True)
if change_bg:
    bg_color_choice = st.sidebar.selectbox("Choose Background Color", ["White", "Green", "Blue", "Black", "Red"])
    color_map = {"White": "#FFFFFF", "Green": "#00FF00", "Blue": "#0000FF", "Black": "#000000", "Red": "#FF0000"}
    selected_color = color_map[bg_color_choice]

apply_comp = st.sidebar.checkbox("📉 Strict File Size Limit (KB)?", value=True)
if apply_comp:
    max_kb = st.sidebar.number_input("Maximum Size (KB)", value=20, step=5)

# Main Dashboard
uploaded_file = st.file_uploader("📂 Upload ZIP file containing images", type=["zip"])

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
                            
                            if change_bg:
                                img = img.convert("RGBA")
                                bg_layer = Image.new("RGBA", img.size, selected_color)
                                current_img = Image.alpha_composite(bg_layer, img).convert("RGB")
                            else:
                                current_img = img.convert("RGB")
                                
                            if change_dim:
                                current_img = current_img.resize((int(width), int(height)), Image.Resampling.LANCZOS)
                                
                            img_byte_arr = io.BytesIO()
                            if apply_comp:
                                img_quality = 90
                                while img_quality > 10:
                                    img_byte_arr = io.BytesIO()
                                    current_img.save(img_byte_arr, format="JPEG", quality=img_quality)
                                    if img_byte_arr.tell() <= (max_kb * 1024):
                                        break
                                    img_quality -= 5
                            else:
                                current_img.save(img_byte_arr, format="JPEG", quality=85)
                            
                            clean_name = os.path.basename(file_name)
                            name_without_ext = os.path.splitext(clean_name)[0]
                            if clean_name:
                                out_zip.writestr(f"processed_{name_without_ext}.jpg", img_byte_arr.getvalue())
                                count += 1
                        except:
                            pass

            if count > 0:
                st.balloons()
                st.success(f"Mubarak ho! Tamam {count} photos ready hain.")
                st.download_button(
                    label="📥 DOWNLOAD PROCESSED ZIP FILE",
                    data=output_buffer.getvalue(),
                    file_name="PicShrink_Output.zip",
                    mime="application/zip"
                )
