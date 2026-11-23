"""Campus image processing lab: uploaded images stay in memory."""
from io import BytesIO
from threading import Lock
from time import perf_counter
import warnings

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_file
from PIL import Image, ImageOps, UnidentifiedImageError

app = Flask(__name__)
MAX_FILE = 5 * 1024 * 1024
MAX_PIXELS = 16_000_000
MAX_SIDE = 1600
# The recommended deployment uses one worker and two threads. Serializing
# decoding keeps two large PNG buffers from being expanded simultaneously.
decode_lock = Lock()
# Multipart framing is allowed in addition to the file limit.
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE + 64 * 1024


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify(status="ok")


def error_response(message, status):
    # Native form navigation accepts HTML; API/fetch clients continue to receive JSON.
    if request.accept_mimetypes.best_match(["text/html", "application/json"]) == "text/html":
        return render_template("index.html", error=message), status
    return jsonify(error=message), status


@app.post("/api/process")
def process():
    started = perf_counter()
    upload = request.files.get("image")
    if not upload or not upload.filename:
        return error_response("이미지 파일을 선택해 주세요.", 400)
    data = upload.stream.read(MAX_FILE + 1)
    if not data:
        return error_response("빈 파일은 처리할 수 없습니다.", 400)
    if len(data) > MAX_FILE:
        return error_response("이미지는 5 MiB 이하여야 합니다.", 413)
    operation = request.form.get("operation", "")
    if operation not in {"grayscale", "blur", "canny"}:
        return error_response("지원하지 않는 처리 방식입니다.", 400)
    try:
        kernel = int(request.form.get("kernel", "3"))
    except ValueError:
        return error_response("커널 크기는 3~51의 홀수여야 합니다.", 400)
    if kernel < 3 or kernel > 51 or kernel % 2 == 0:
        return error_response("커널 크기는 3~51의 홀수여야 합니다.", 400)

    try:
        with decode_lock:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as image:
                    if image.format not in {"JPEG", "PNG"}:
                        return error_response("JPEG 또는 PNG 이미지만 지원합니다.", 400)
                    width, height = image.size
                    if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
                        return error_response("원본 이미지는 1,600만 픽셀 이하여야 합니다.", 400)
                    image.verify()
                with Image.open(BytesIO(data)) as image:
                    # JPEG draft requests decoder-side downsampling before pixel decoding.
                    # PNG does not support draft and may still require a full decode.
                    if image.format == "JPEG":
                        image.draft("RGB", (MAX_SIDE, MAX_SIDE))
                    image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS, reducing_gap=3.0)
                    oriented = ImageOps.exif_transpose(image)
                    rgb = oriented.convert("RGB")
                    pixels = np.asarray(rgb)
    except (UnidentifiedImageError, OSError, ValueError, EOFError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        return error_response("올바른 JPEG 또는 PNG 파일을 선택해 주세요.", 400)
    except MemoryError:
        return error_response("이미지를 처리할 메모리가 부족합니다. 더 작은 이미지를 선택해 주세요.", 500)

    try:
        compute_start = perf_counter()
        if operation == "grayscale":
            result = cv2.cvtColor(pixels, cv2.COLOR_RGB2GRAY)
        elif operation == "blur":
            result = cv2.GaussianBlur(pixels, (kernel, kernel), 0)
        else:
            result = cv2.Canny(cv2.cvtColor(pixels, cv2.COLOR_RGB2GRAY), 100, 200)
        compute_ms = (perf_counter() - compute_start) * 1000
        if operation == "blur":
            result = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
        ok, encoded = cv2.imencode(".png", result)
    except (cv2.error, MemoryError):
        app.logger.exception("Image processing failed")
        return error_response("이미지를 처리할 수 없습니다. 더 작은 이미지를 다시 선택해 주세요.", 500)
    if not ok:
        return error_response("결과 이미지를 만들 수 없습니다.", 500)
    output = BytesIO(encoded.tobytes())
    response = send_file(output, mimetype="image/png", download_name="result.png")
    response.headers["X-Compute-Ms"] = f"{compute_ms:.3f}"
    response.headers["X-Processing-Ms"] = f"{(perf_counter() - started) * 1000:.3f}"
    response.headers["X-Original-Width"] = str(width)
    response.headers["X-Original-Height"] = str(height)
    response.headers["X-Processed-Width"] = str(pixels.shape[1])
    response.headers["X-Processed-Height"] = str(pixels.shape[0])
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(413)
def too_large(_error):
    return error_response("요청 크기가 너무 큽니다. 5 MiB 이하 이미지를 선택해 주세요.", 413)


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error="요청한 페이지를 찾을 수 없습니다."), 404


if __name__ == "__main__":
    app.run(port=5000)
