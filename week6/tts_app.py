"""Local Piper TTS lab. The voice is loaded lazily and cached per process."""
from io import BytesIO
from pathlib import Path
from threading import Lock
from time import perf_counter
import math
import re
import wave

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
MODEL = Path(__file__).resolve().parent / "models" / "en_US-lessac-low.onnx"
_voice = None
_voice_lock = Lock()
_synth_lock = Lock()


def get_voice():
    global _voice
    if not MODEL.is_file() or not Path(str(MODEL) + ".json").is_file():
        raise FileNotFoundError("모델 파일(.onnx 및 .onnx.json)이 없습니다. README의 다운로드 명령을 실행해 주세요.")
    with _voice_lock:
        if _voice is None:
            from piper import PiperVoice
            _voice = PiperVoice.load(str(MODEL))
        return _voice


@app.get("/tts")
def index():
    return render_template("tts.html")


@app.post("/api/tts")
def synthesize():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="JSON 형식으로 요청해 주세요."), 400
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        return jsonify(error="영어 문장을 입력해 주세요."), 400
    text = text.strip()
    if len(text) > 500:
        return jsonify(error="영어 문장은 500자 이하여야 합니다."), 400
    if not re.fullmatch(r"[A-Za-z0-9\s.,!?;:'\"()\-]+", text) or not re.search(r"[A-Za-z]", text):
        return jsonify(error="영문자와 일반 문장 부호로 입력해 주세요."), 400
    try:
        scale = float(payload.get("length_scale", 1.0))
        if not math.isfinite(scale) or not 0.5 <= scale <= 2.0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify(error="속도 값은 0.5~2.0이어야 합니다."), 400
    try:
        started = perf_counter()
        voice = get_voice()
        from piper import SynthesisConfig
        buffer = BytesIO()
        with _synth_lock:
            with wave.open(buffer, "wb") as wav:
                voice.synthesize_wav(text, wav, syn_config=SynthesisConfig(length_scale=scale))
        generated_ms = (perf_counter() - started) * 1000
        buffer.seek(0)
        with wave.open(buffer, "rb") as wav:
            duration = wav.getnframes() / wav.getframerate()
        size = buffer.getbuffer().nbytes
        buffer.seek(0)
        response = send_file(buffer, mimetype="audio/wav", download_name="speech.wav")
        response.headers["X-Generation-Ms"] = f"{generated_ms:.3f}"
        response.headers["X-Audio-Duration"] = f"{duration:.3f}"
        response.headers["X-Audio-Bytes"] = str(size)
        response.headers["Cache-Control"] = "no-store"
        return response
    except (FileNotFoundError, ImportError) as exc:
        return jsonify(error=str(exc) or "Piper를 설치해 주세요."), 503
    except Exception:
        app.logger.exception("Piper synthesis failed")
        return jsonify(error="음성 생성에 실패했습니다. 모델과 Piper 설치를 확인해 주세요."), 500


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="요청 크기가 너무 큽니다."), 413


if __name__ == "__main__":
    app.run(port=5000)
