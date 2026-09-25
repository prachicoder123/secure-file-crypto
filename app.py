"""
app.py
------
Flask web server for the Secure File Encryption & Decryption Tool.
Provides a simple local-hosted UI to encrypt/decrypt files with AES-256-GCM.
"""

import os
import uuid
from flask import Flask, render_template, request, send_file, jsonify, after_this_request

from crypto_utils import encrypt_file, decrypt_file, DecryptionError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ENCRYPTED_DIR = os.path.join(BASE_DIR, "encrypted")
DECRYPTED_DIR = os.path.join(BASE_DIR, "decrypted")

for d in (UPLOAD_DIR, ENCRYPTED_DIR, DECRYPTED_DIR):
    os.makedirs(d, exist_ok=True)

MAX_FILE_SIZE_MB = 100

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024


def safe_temp_path(directory: str, original_filename: str) -> str:
    """Build a collision-free temp path while keeping the original extension."""
    unique = uuid.uuid4().hex
    _, ext = os.path.splitext(original_filename)
    return os.path.join(directory, f"{unique}{ext}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/encrypt", methods=["POST"])
def encrypt_route():
    file = request.files.get("file")
    password = request.form.get("password", "")

    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400

    input_path = safe_temp_path(UPLOAD_DIR, file.filename)
    file.save(input_path)

    output_filename = file.filename + ".enc"
    output_path = safe_temp_path(ENCRYPTED_DIR, output_filename)

    try:
        encrypt_file(input_path, output_path, password)
    except Exception as e:
        return jsonify({"error": f"Encryption failed: {e}"}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    @after_this_request
    def cleanup(response):
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass
        return response

    return send_file(output_path, as_attachment=True, download_name=output_filename)


@app.route("/decrypt", methods=["POST"])
def decrypt_route():
    file = request.files.get("file")
    password = request.form.get("password", "")

    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400

    input_path = safe_temp_path(UPLOAD_DIR, file.filename)
    file.save(input_path)

    # Strip the .enc extension if present, otherwise prefix "decrypted_"
    original_name = file.filename
    if original_name.endswith(".enc"):
        output_filename = original_name[:-4]
    else:
        output_filename = "decrypted_" + original_name

    output_path = safe_temp_path(DECRYPTED_DIR, output_filename)

    try:
        decrypt_file(input_path, output_path, password)
    except DecryptionError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {e}"}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

    @after_this_request
    def cleanup(response):
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass
        return response

    return send_file(output_path, as_attachment=True, download_name=output_filename)


if __name__ == "__main__":
    print("=" * 60)
    print(" Secure File Encryption & Decryption Tool")
    print(" Running at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
