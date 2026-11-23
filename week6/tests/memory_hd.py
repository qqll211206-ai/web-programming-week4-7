"""Optional memory smoke test: python week6/tests/memory_hd.py (requires psutil)."""
import gc
import io
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import psutil
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app, MAX_FILE

buf = io.BytesIO()
image = Image.new("RGBA", (4000, 4000), (80, 140, 60, 255))
image.save(buf, format="PNG")
image.close()
payload = buf.getvalue()
assert len(payload) < MAX_FILE
del image, buf
gc.collect()
process = psutil.Process(os.getpid())
peak = [process.memory_info().rss]
stop = threading.Event()


def sample():
    while not stop.wait(0.01):
        peak[0] = max(peak[0], process.memory_info().rss)


def process_once(_):
    with app.test_client() as client:
        response = client.post("/api/process", data={
            "image": (io.BytesIO(payload), "large.png"), "operation": "canny", "kernel": "3",
        })
        assert response.status_code == 200, response.status_code
        assert response.headers["X-Processed-Width"] == "1600"
        return len(response.data)


process_once(0)
gc.collect()
warm = process.memory_info().rss
worker = threading.Thread(target=sample, daemon=True)
worker.start()
rss_after_rounds = []
try:
    with ThreadPoolExecutor(max_workers=2) as pool:
        for _ in range(3):
            list(pool.map(process_once, range(4)))
            gc.collect()
            rss_after_rounds.append(process.memory_info().rss)
finally:
    stop.set()
    worker.join()
print("12 requests, 2 concurrent, 4000x4000 RGBA PNG: all HTTP 200")
print("warm RSS MiB:", round(warm / 1048576, 1))
print("peak RSS MiB:", round(peak[0] / 1048576, 1))
print("RSS after each round MiB:", [round(n / 1048576, 1) for n in rss_after_rounds])
print("Local test only; not a Render memory measurement.")

