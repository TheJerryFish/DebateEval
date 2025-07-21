from flask import Flask, render_template, request
import os
from main import process_mp3_file  # updated to use your actual logic function

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".mp3"):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            
            # Run your logic using the function from main.py
            result_text = process_mp3_file(filepath, output_dir=OUTPUT_FOLDER)

            return render_template("index.html", result=result_text)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)