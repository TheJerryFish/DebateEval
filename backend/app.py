from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from main import process_mp3_file  # your analysis pipeline

app = Flask(__name__)
CORS(app)  # enable cross-origin access from React frontend

UPLOAD_FOLDER = 'backend/static/uploads'
OUTPUT_FOLDER = 'backend/static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename.endswith(".mp3"):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # This should return a dictionary with transcript, plot filenames, table data, etc.
        result = process_mp3_file(filepath, output_dir=OUTPUT_FOLDER)

        return jsonify({
            "transcript": result.get("transcript", ""),
            "table_data": result.get("table", []),
            "tone_plot": f"/static/output/{result.get('tone_plot', 'plot.png')}",
            "smoothed_plot": f"/static/output/{result.get('smoothed_plot', 'smoothed_plot.png')}",
            "metrics": result.get("metrics", {})
        })

    return jsonify({"error": "Invalid file type"}), 400

@app.route("/static/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)