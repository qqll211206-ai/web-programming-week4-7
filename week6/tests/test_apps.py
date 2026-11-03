"""Run with: python -m unittest discover -s week6/tests -v"""
import io
import os
import sys
import unittest
from unittest.mock import patch

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as image_app
import tts_app


def png(width=120, height=90):
    frame = np.zeros((height, width, 3), np.uint8)
    frame[:, width // 2:] = (30, 120, 230)
    ok, data = cv2.imencode(".png", frame)
    assert ok
    return data.tobytes()


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.client = image_app.app.test_client()

    def post(self, payload, operation="grayscale", kernel="3", filename="test.png"):
        return self.client.post("/api/process", data={"image": (io.BytesIO(payload), filename), "operation": operation, "kernel": kernel})

    def test_operations_return_valid_png(self):
        for operation in ("grayscale", "blur", "canny"):
            with self.subTest(operation=operation):
                response = self.post(png(), operation)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "image/png")
                result = cv2.imdecode(np.frombuffer(response.data, np.uint8), cv2.IMREAD_UNCHANGED)
                self.assertEqual(result.shape[:2], (90, 120))
                self.assertGreaterEqual(float(response.headers["X-Compute-Ms"]), 0)
                self.assertGreaterEqual(float(response.headers["X-Processing-Ms"]), 0)

    def test_rejections(self):
        self.assertEqual(self.client.post("/api/process").status_code, 400)
        self.assertEqual(self.post(b"").status_code, 400)
        self.assertEqual(self.post(b"not an image").status_code, 400)
        self.assertEqual(self.post(png(), "unknown").status_code, 400)
        self.assertEqual(self.post(png(), "blur", "4").status_code, 400)
        self.assertEqual(self.post(b"x" * (5 * 1024 * 1024 + 1)).status_code, 413)
        self.assertEqual(self.post(png(3000, 3000)).status_code, 400)
        self.assertEqual(self.client.get("/not-found").status_code, 404)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_large_image_resizes(self):
        response = self.post(png(2400, 1800), "blur", "31")
        self.assertEqual(response.status_code, 200)
        result = cv2.imdecode(np.frombuffer(response.data, np.uint8), cv2.IMREAD_UNCHANGED)
        self.assertEqual(result.shape[:2], (1200, 1600))


class TTSTests(unittest.TestCase):
    def setUp(self):
        self.client = tts_app.app.test_client()

    def test_bad_input(self):
        for payload in ({}, {"text": ""}, {"text": "x" * 501}, {"text": "안녕하세요"}, {"text": "Hello", "length_scale": 3}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/tts", json=payload).status_code, 400)

    def test_missing_model(self):
        with patch.object(tts_app, "MODEL", tts_app.MODEL.parent / "does-not-exist.onnx"):
            response = self.client.post("/api/tts", json={"text": "Hello campus."})
            self.assertEqual(response.status_code, 503)
            self.assertIn("모델", response.json["error"])

if __name__ == "__main__":
    unittest.main()
