from flask import Flask, render_template, request
from adap2.validator import validate_certificate
import os

app = Flask(__name__, template_folder=".")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def validate():
    file = request.files.get("file")
    if not file:
        return render_template("index.html", error="No file uploaded")

    filename = file.filename
    if filename == "":
        return render_template("index.html", error="No file selected")

    upload_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(upload_path)

    try:
        result = validate_certificate(upload_path)
        return render_template("index.html", result=result)
    except Exception as e:
        return render_template("index.html", error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
