"""Campus image processing lab: uploaded images stay in memory."""
from io import BytesIO
from time import perf_counter
import warnings

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
MAX_FILE = 5 * 1024 * 1024
MAX_PIXELS = 8_000_000
MAX_SIDE = 1600
# Multipart framing is allowed in addition to the file limit.
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE + 64 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.post("/api/process")
def process():
    started = perf_counter()
    upload = request.files.get("image")
    if not upload or not upload.filename:
        return jsonify(error="이미지 파일을 선택해 주세요."), 400
    data = upload.stream.read(MAX_FILE + 1)
    if not data:
        return jsonify(error="빈 파일은 처리할 수 없습니다."), 400
    if len(data) > MAX_FILE:
        return jsonify(error="이미지는 5 MiB 이하여야 합니다."), 413
    operation = request.form.get("operation", "")
    if operation not in {"grayscale", "blur", "canny"}:
        return jsonify(error="지원하지 않는 처리 방식입니다."), 400
    try:
        kernel = int(request.form.get("kernel", "3"))
    except ValueError:
        return jsonify(error="커널 크기는 3~51의 홀수여야 합니다."), 400
    if kernel < 3 or kernel > 51 or kernel % 2 == 0:
        return jsonify(error="커널 크기는 3~51의 홀수여야 합니다."), 400

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format not in {"JPEG", "PNG"}:
                    return jsonify(error="JPEG 또는 PNG 이미지만 지원합니다."), 400
                width, height = image.size
                if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
                    return jsonify(error="이미지는 800만 픽셀 이하여야 합니다."), 400
                image.verify()
        pixels = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if pixels is None:
            raise ValueError("decode failed")
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        return jsonify(error="올바른 JPEG 또는 PNG 파일을 선택해 주세요."), 400

    height, width = pixels.shape[:2]
    if max(width, height) > MAX_SIDE:
        scale = MAX_SIDE / max(width, height)
        pixels = cv2.resize(pixels, (max(1, round(width * scale)), max(1, round(height * scale))), interpolation=cv2.INTER_AREA)
    compute_start = perf_counter()
    if operation == "grayscale":
        result = cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY)
    elif operation == "blur":
        result = cv2.GaussianBlur(pixels, (kernel, kernel), 0)
    else:
        result = cv2.Canny(cv2.cvtColor(pixels, cv2.COLOR_BGR2GRAY), 100, 200)
    compute_ms = (perf_counter() - compute_start) * 1000
    ok, encoded = cv2.imencode(".png", result)
    if not ok:
        return jsonify(error="결과 이미지를 만들 수 없습니다."), 500
    output = BytesIO(encoded.tobytes())
    response = send_file(output, mimetype="image/png", download_name="result.png")
    response.headers["X-Compute-Ms"] = f"{compute_ms:.3f}"
    response.headers["X-Processing-Ms"] = f"{(perf_counter() - started) * 1000:.3f}"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="요청 크기가 너무 큽니다. 5 MiB 이하 이미지를 선택해 주세요."), 413


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="요청한 페이지를 찾을 수 없습니다."), 404


if __name__ == "__main__":
    app.run(port=5000)
