"""Run with: python -m unittest discover -s week6/tests -v"""
import io
import os
import sys
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image, ImageDraw

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
        disguised = io.BytesIO()
        Image.new("RGB", (10, 10)).save(disguised, format="GIF")
        self.assertEqual(self.post(disguised.getvalue(), filename="fake.jpg").status_code, 400)
        self.assertEqual(self.post(png(), "unknown").status_code, 400)
        self.assertEqual(self.post(png(), "blur", "4").status_code, 400)
        self.assertEqual(self.post(b"x" * (5 * 1024 * 1024 + 1)).status_code, 413)
        self.assertEqual(self.post(png(4001, 4000)).status_code, 400)
        self.assertEqual(self.client.get("/not-found").status_code, 404)
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})

    def test_large_image_resizes(self):
        response = self.post(png(2400, 1800), "blur", "31")
        self.assertEqual(response.status_code, 200)
        result = cv2.imdecode(np.frombuffer(response.data, np.uint8), cv2.IMREAD_UNCHANGED)
        self.assertEqual(result.shape[:2], (1200, 1600))

    def test_phone_photos_and_orientation(self):
        for size, fmt, orientation, expected in (
            ((1920, 1080), "JPEG", None, (1600, 900)),
            ((4032, 3024), "JPEG", None, (1600, 1200)),
            ((3024, 4032), "JPEG", 6, (1600, 1200)),
            ((4000, 3000), "PNG", None, (1600, 1200)),
        ):
            with self.subTest(size=size, format=fmt, orientation=orientation):
                image = Image.new("RGB", size, (20, 40, 60))
                # After a 90-degree clockwise EXIF rotation, this patch moves to the top right.
                ImageDraw.Draw(image).rectangle((0, 0, size[0] // 3, size[1] // 3), fill=(240, 20, 20))
                buffer = io.BytesIO()
                exif = Image.Exif()
                if orientation:
                    exif[274] = orientation
                image.save(buffer, format=fmt, exif=exif)
                image.close()
                self.assertLess(len(buffer.getvalue()), image_app.MAX_FILE)
                response = self.post(buffer.getvalue(), "blur", "3", "phone.jpg" if fmt == "JPEG" else "phone.png")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.mimetype, "image/png")
                with Image.open(io.BytesIO(response.data)) as result:
                    self.assertEqual(result.size, expected)
                    if orientation:
                        red = result.getpixel((expected[0] - 100, 100))
                        dark = result.getpixel((100, 100))
                        self.assertGreater(red[0], 180)
                        self.assertLess(dark[0], 80)
                self.assertEqual(int(response.headers["X-Original-Width"]), size[0])
                self.assertEqual(int(response.headers["X-Original-Height"]), size[1])
                self.assertEqual(int(response.headers["X-Processed-Width"]), expected[0])
                self.assertEqual(int(response.headers["X-Processed-Height"]), expected[1])
                print(f"  {fmt} {size} EXIF={orientation} -> {expected}: HTTP {response.status_code}")

    def test_errors_for_fetch_and_native_form(self):
        for accept in ("application/json", "text/html"):
            for body in (b"invalid image", b"x" * (image_app.MAX_FILE + 1)):
                response = self.client.post("/api/process", data={"image": (io.BytesIO(body), "fake.jpg"),
                    "operation": "canny", "kernel": "3"}, headers={"Accept": accept})
                self.assertEqual(response.status_code, 400 if len(body) < 100 else 413)
                self.assertEqual(response.mimetype, "text/html" if accept == "text/html" else "application/json")
                if accept == "text/html":
                    self.assertIn(b'id="image-form"', response.data)
                else:
                    self.assertIn("error", response.get_json())

    def test_iphone_resolution_all_operations(self):
        data = io.BytesIO()
        with Image.new("RGB", (4032, 3024), (30, 90, 150)) as image:
            image.save(data, format="JPEG")
        for operation in ("grayscale", "blur", "canny"):
            with self.subTest(operation=operation):
                response = self.post(data.getvalue(), operation, "3", "iphone.jpg")
                self.assertEqual(response.status_code, 200)
                with Image.open(io.BytesIO(response.data)) as result:
                    self.assertEqual(result.size, (1600, 1200))
                print(f"  JPEG (4032, 3024) {operation} -> (1600, 1200): HTTP 200")


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
