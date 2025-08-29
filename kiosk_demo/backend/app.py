# backend/app.py
import os
import json
import unicodedata
import re
from flask import Flask, send_from_directory, jsonify, abort, request
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Flask sẽ phục vụ folder frontend làm static files
app = Flask(__name__, static_folder="../frontend", template_folder="../frontend")
CORS(app)

# Thư mục chứa benh_ly.json (app.py đang nằm trong backend/)
DATA_DIR = os.path.join(app.root_path, "data")
BENHLY_PATH = os.path.join(DATA_DIR, "benh_ly.json")

# Đường dẫn model, sửa lại cho đúng nếu cần
model_dir = "e:/KioskMedical/kiosk-health-test"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir)
id2label = {
    0: "Tự theo dõi",
    1: "Chuyển tuyến",
    2: "Nhập viện"
}
def slugify(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFD", s)
    s = s.encode("ascii", "ignore").decode("ascii")   # bỏ dấu
    s = s.lower()
    s = re.sub(r'[\/–—]+', '-', s)                    # đổi dấu / hoặc – thành -
    s = re.sub(r'[^a-z0-9\s\-]', '', s)               # loại ký tự lạ
    s = re.sub(r'\s+', '-', s).strip('-')
    return s

def du_doan(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        pred = torch.argmax(logits, dim=1).item()
    return id2label[pred]

# Root -> mở categories.html
@app.route("/")
def index():
    return app.send_static_file("categories.html")

# Phục vụ các file tĩnh (categories.html, subcategory.html, css, js)
@app.route("/<path:filename>")
def static_files(filename):
    return app.send_static_file(filename)

# Nếu bạn muốn vẫn cho phép truy cập nguyên bản file JSON:
@app.route("/data/benh_ly.json")
def benh_ly_json():
    return send_from_directory(DATA_DIR, "benh_ly.json")

# API: danh sách nhóm (unique)
@app.route("/api/groups")
def api_groups():
    try:
        with open(BENHLY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"error": "Không đọc được file dữ liệu."}), 500

    seen = set()
    groups = []
    for item in data:
        g = (item.get("Nhóm hệ cơ quan") or "").strip()
        if g and g not in seen:
            seen.add(g)
            groups.append({"group": g, "slug": slugify(g)})
    return jsonify({"groups": groups})

# API: triệu chứng theo slug của nhóm
@app.route("/api/symptoms/<slug>")
def api_symptoms(slug):
    try:
        with open(BENHLY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return jsonify({"error": "Không đọc được file dữ liệu."}), 500

    # tìm tên nhóm gốc tương ứng slug
    groups_map = {}
    for item in data:
        g = (item.get("Nhóm hệ cơ quan") or "").strip()
        if g:
            groups_map.setdefault(slugify(g), g)

    if slug not in groups_map:
        return jsonify({"error": "Không tìm thấy nhóm hệ cơ quan"}), 404

    group_name = groups_map[slug]
    symptoms = []
    for item in data:
        if (item.get("Nhóm hệ cơ quan") or "").strip() == group_name:
            symptoms.append({
                "triệu_chứng": item.get("triệu_chứng"),
                "mô_tả": item.get("Từ đồng nghĩa / mô tả bổ sung", "")
            })

    return jsonify({"group": group_name, "symptoms": symptoms})

# API: dự đoán theo triệu chứng
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    symptoms = data.get("symptoms", [])
    if not symptoms:
        return jsonify({"result": "Không có triệu chứng."})
    input_text = ", ".join(symptoms)
    result = du_doan(input_text)
    return jsonify({"result": result})

if __name__ == "__main__":
    # chạy ở localhost:5000
    app.run(debug=True, host="127.0.0.1", port=5000)
