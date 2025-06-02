import streamlit as st
import numpy as np
import cv2
import json
from PIL import Image
import io
import base64

# 載入語意色彩設定（使用 Lab 模式）
with open("color_moods.json", "r", encoding="utf-8") as f:
    color_moods = json.load(f)

# Lab 濾鏡處理函式
def apply_lab_filter(image, l_shift, a_shift, b_shift):
    img = np.array(image)
    img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.int16)

    # 拆開頻道
    l, a, b = cv2.split(img_lab)

    # 加上色彩偏移量
    l = np.clip(l + l_shift, 0, 255)
    a = np.clip(a + a_shift, 0, 255)
    b = np.clip(b + b_shift, 0, 255)

    # 合併並轉回 RGB
    img_lab = cv2.merge((l, a, b)).astype(np.uint8)
    filtered_img = cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB)
    return filtered_img

# 下載圖片的 HTML 連結

def get_image_download_link(img_array, filename="filtered.png"):
    buffered = io.BytesIO()
    Image.fromarray(img_array).save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:file/png;base64,{b64}" download="{filename}">⬇️ 點我下載濾鏡圖片</a>'

# --- Streamlit 開始 ---
st.title("🎨 ColorMood 最懂你的歌詞濾鏡 ")

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
        l_shift = cfg.get("l_shift", 0)
        a_shift = cfg.get("a_shift", 0)
        b_shift = cfg.get("b_shift", 0)
        st.session_state.reset = False
    else:
        l_shift = st.slider("✨ 明度 L* 偏移", -50, 50, int(cfg.get("l_shift", 0)))
        a_shift = st.slider("🔴 a* 紅綠偏移", -50, 50, int(cfg.get("a_shift", 0)))
        b_shift = st.slider("🔵 b* 藍黃偏移", -50, 50, int(cfg.get("b_shift", 0)))

    # 濾鏡處理
    filtered_img = apply_lab_filter(image, l_shift, a_shift, b_shift)
    filtered_img = np.clip(filtered_img, 0, 255).astype(np.uint8)

    # 顯示前後對比圖
    st.subheader("🖼️ 處理結果對比")
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="原圖", use_container_width=True)
    with col2:
        st.image(filtered_img, caption="濾鏡後", use_container_width=True)

    # 下載按鈕
    st.markdown("---")
    st.markdown(get_image_download_link(filtered_img, filename="colormood_output.png"), unsafe_allow_html=True)
