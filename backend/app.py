import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot import chatbot_response, search_faq

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"answer": "Bitte gib eine Frage ein."}), 400
    answer = chatbot_response(msg)
    return jsonify({"answer": answer})

@app.route("/faq", methods=["POST"])
def faq():
    data = request.get_json() or {}
    msg = data.get("message", "").strip()
    answer = search_faq(msg)
    return jsonify({"answer": answer})

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
