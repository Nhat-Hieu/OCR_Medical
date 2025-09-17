import base64, json, pathlib, tempfile, requests

BASE_URL = "http://192.168.1.197:1234/v1"
MODEL_ID = "qwen/qwen2.5-vl-7b"

def infer_mime_from_filename(filename: str) -> str:
    low = filename.lower()
    if low.endswith(".png"):
        return "image/png"
    if low.endswith(".webp"):
        return "image/webp"
    if low.endswith(".jpg") or low.endswith(".jpeg"):
        return "image/jpeg"
    return "application/octet-stream"

def to_data_url(path: str) -> str:
    mime = infer_mime_from_filename(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def call_qwen_ocr(image_path: str, prompt_text: str) -> str:
    url = f"{BASE_URL}/chat/completions"
    image_url = to_data_url(image_path)  # gửi ảnh base64

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt_text},
                    {"type": "input_image", "image_url": {"url": image_url}},
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1500,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
