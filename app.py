import streamlit as st
import numpy as np
import cv2
import json
from PIL import Image
import io
import base64

# 載入語意色彩設定
with open("color_moods.json", "r", encoding="utf-8") as f:
    color_moods = json.load(f)

# HSV 濾鏡
def apply_hsv_filter(image, hue_shift, saturation_scale, brightness_scale):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    img[..., 0] = (img[..., 0] + hue_shift) % 180
    img[..., 1] *= saturation_scale
    img[..., 2] *= brightness_scale
    img = np.clip(img, 0, 255).astype(np.uint8)
    return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)

# 對比度調整
def adjust_contrast(image, contrast_scale):
    return np.clip(128 + contrast_scale * (image - 128), 0, 255).astype(np.uint8)

# 色溫調整
def adjust_color_temperature(img, warm_shift):
    img = img.copy()
    b, g, r = cv2.split(img)

    # 修正這裡的加減法
    r = np.clip(r.astype(np.int16) + warm_shift, 0, 255).astype(np.uint8)
    b = np.clip(b.astype(np.int16) - warm_shift, 0, 255).astype(np.uint8)

    return cv2.merge((b, g, r))

# 下載圖片的 HTML 連結
def get_image_download_link(img_array, filename="filtered.png"):
    buffered = io.BytesIO()
    Image.fromarray(img_array).save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:file/png;base64,{b64}" download="{filename}">⬇️ 點我下載濾鏡圖片</a>'

# --- Streamlit 開始 ---
st.title("🎨 ColorMood 濾鏡生成器 ")

uploaded_file = st.file_uploader("請上傳一張圖片", type=["jpg", "png"])
mood = st.selectbox("請選擇風格關鍵字（情境／情緒）", list(color_moods.keys()))

if uploaded_file and mood:
    image = Image.open(uploaded_file).convert("RGB")
    cfg = color_moods[mood]

    # 初始狀態處理
    if "reset" not in st.session_state:
        st.session_state.reset = False

    if st.button("🔁 還原預設濾鏡設定"):
        st.session_state.reset = True

    # 讀取預設值或使用者選項
    if st.session_state.reset:
        hue_shift = cfg.get("hue", 0)
        saturation_scale = cfg.get("saturation", 1.0)
        brightness_scale = cfg.get("brightness", 1.0)
        contrast_scale = cfg.get("contrast", 1.0)
        warm_shift = cfg.get("warm_shift", 0)
        st.session_state.reset = False
    else:
        hue_shift = st.slider("🎨 色調偏移 Hue", -90, 90, int(cfg.get("hue", 0)))
        saturation_scale = st.slider("🌈 飽和度倍率", 0.0, 2.0, float(cfg.get("saturation", 1.0)), 0.1)
        brightness_scale = st.slider("💡 亮度倍率", 0.0, 2.0, float(cfg.get("brightness", 1.0)), 0.1)
        contrast_scale = st.slider("🧪 對比度倍率", 0.5, 2.0, float(cfg.get("contrast", 1.0)), 0.1)
        warm_shift = st.slider("🔥 色溫偏移值", -50, 50, int(cfg.get("warm_shift", 0)))

    # 濾鏡處理順序
    filtered_img = apply_hsv_filter(image, hue_shift, saturation_scale, brightness_scale)
    filtered_img = adjust_contrast(filtered_img, contrast_scale)
    filtered_img = adjust_color_temperature(filtered_img, warm_shift)

    # 顯示前後對比圖
    st.subheader("🖼️ 處理結果對比")
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="原圖", use_column_width=True)
    with col2:
        st.image(filtered_img, caption="濾鏡後", use_column_width=True)

    # 下載按鈕
    st.markdown("---")
    st.markdown(get_image_download_link(filtered_img, filename="colormood_output.png"), unsafe_allow_html=True)
