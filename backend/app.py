# app.py
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import os
import sys
import json
import time
from main import process_mp3_file

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".mp3"):
        return jsonify({"error": "Invalid file type"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    def generate():
        # Stream progress messages
        yield "data: Starting analysis...\n\n"
        result = {}
        for msg, partial_result in process_mp3_file(filepath, OUTPUT_FOLDER, stream=True):
            # Send progress message
            yield f"data: {msg}\n\n"
            result.update(partial_result or {})
        # Finally send the full result as JSON
        yield f"data: DONE::{json.dumps(result)}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/static/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)