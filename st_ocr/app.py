# =========================
# 0) IMPORTS
# =========================
import os
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import streamlit as st

# =========================
# 1) HÀM TIỆN ÍCH (pipeline tự động)
# =========================
def auto_invert_if_needed(bgr_img):
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    if gray.mean() < 120:
        return cv2.bitwise_not(bgr_img)
    return bgr_img

def noise_removal(image):
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.erode(image, kernel, iterations=1)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    image = cv2.medianBlur(image, 3)
    return image

def thin_font(image):
    inv = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    eroded = cv2.erode(inv, kernel, iterations=1)
    return cv2.bitwise_not(eroded)

def thick_font(image):
    inv = cv2.bitwise_not(image)
    kernel = np.ones((2,2),np.uint8)
    dilated = cv2.dilate(inv, kernel, iterations=1)
    return cv2.bitwise_not(dilated)

def sharpness_score(img_bin):
    return cv2.Laplacian(img_bin, cv2.CV_64F).var()

def preprocess_image(cv_img):
    # Tự động quyết định đảo màu
    img_proc = auto_invert_if_needed(cv_img)

    # Xám & nhị phân
    gray = cv2.cvtColor(img_proc, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )

    # Khử nhiễu
    no_noise = noise_removal(bw)

    # Chọn phiên bản tốt nhất
    eroded = thin_font(no_noise)
    dilated = thick_font(no_noise)
    candidates = {
        "no_noise": (no_noise, sharpness_score(no_noise)),
        "thin":     (eroded, sharpness_score(eroded)),
        "thick":    (dilated, sharpness_score(dilated)),
    }
    final_name, (final_img, _) = max(candidates.items(), key=lambda kv: kv[1][1])
    return final_img

# =========================
# 2) STREAMLIT UI
# =========================
st.set_page_config(page_title="OCR Bệnh Án", layout="wide")
st.title("📄 OCR Bệnh Án - Tự động")

# Sidebar: upload ảnh và lưu kết quả
uploaded_file = st.sidebar.file_uploader("📁 Tải ảnh lên", type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'])
save_option = st.sidebar.checkbox("💾 Lưu kết quả OCR", value=True)

if uploaded_file is not None:
    # Đọc ảnh
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    cv_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Hiển thị ảnh gốc
    st.image(cv_img, caption="Ảnh gốc", use_column_width=True)

    # OCR pipeline
    final_img = preprocess_image(cv_img)
    ocr = PaddleOCR(lang='vi', use_angle_cls=True, rec_char_type='vi')
    result = ocr.ocr(final_img)

    # Hiển thị text OCR
    st.subheader("📄 Kết quả OCR")
    CONF_THRESH = 0.40
    extracted_text = ""
    if result and result[0]:
        for line in result[0]:
            txt = line[1][0]
            conf = float(line[1][1])
            if conf >= CONF_THRESH:
                extracted_text += txt + "\n"
        st.text_area("Nội dung nhận diện", extracted_text, height=300)
    else:
        st.warning("❌ Không có text nhận diện được")

    # Lưu kết quả
    if save_option:
        os.makedirs("output", exist_ok=True)
        cv2.imwrite("output/final_image.jpg", final_img)
        txt_path = "output/ocr_result.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        st.success(f"💾 Đã lưu kết quả OCR vào thư mục 'output/'")

else:
    st.info("📌 Vui lòng tải ảnh lên từ sidebar")
