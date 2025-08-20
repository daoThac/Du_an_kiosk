from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# Load dữ liệu từ JSON
with open("backend/data/benh_ly.json", "r", encoding="utf-8") as f:
    data = json.load(f)

@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    # Trả về danh sách tất cả triệu chứng từ JSON
    symptoms = [item["triệu_chứng"] for item in data]
    return jsonify(symptoms)

@app.route("/recommend", methods=["POST"])
def recommend():
    req = request.json
    selected = req.get("symptoms", [])
    results = []

    for symptom in selected:
        for item in data:
            if item["triệu_chứng"] == symptom:
                results.append(item)
                break

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
