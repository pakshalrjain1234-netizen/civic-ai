"""Run with python -m unittest discover -s tests. Route fixtures are test-only."""
import base64
import io
import unittest
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from fastapi.testclient import TestClient
from PIL import Image
import main
from utils.images import decode_frame


def frame():
    buffer = io.BytesIO()
    Image.new('RGB', (80, 60), color=(40, 50, 60)).save(buffer, format='JPEG')
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client_context = TestClient(main.app)
        self.client = self.client_context.__enter__()
        self.original_model = main.detector.model
        self.original_detect = main.detector.detect

    def tearDown(self):
        main.detector.local.model = self.original_model
        main.detector.detect = self.original_detect
        self.client_context.__exit__(None, None, None)

    def test_missing_model_health_and_detection(self):
        main.detector.local.model = None
        health = self.client.get('/health')
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()['status'], 'online')
        self.assertFalse(health.json()['model_loaded'])
        self.assertEqual(health.json()['runtime'], 'onnx')
        self.assertEqual(health.json()['model'], 'civiceye-v2.onnx')
        result = self.client.post('/detect', json={'image': frame()})
        self.assertEqual(result.status_code, 503)
        self.assertEqual(result.json()['error'], 'MODEL_NOT_LOADED')
        self.assertEqual(result.json()['detections'], [])

    def test_real_image_decoding_and_corrupt_input(self):
        image = decode_frame(frame(), main.MAX_BYTES)
        self.assertEqual(image.size, (80, 60))
        with self.assertRaises(ValueError):
            decode_frame('data:image/jpeg;base64,bad!', main.MAX_BYTES)
        main.detector.local.model = object()  # Test-only loaded gate, no YOLO predictions.
        result = self.client.post('/detect', json={'image': 'data:image/jpeg;base64,bad!'})
        self.assertEqual(result.status_code, 400)

    def test_no_model_fallback_and_bounded_upload(self):
        result = self.client.post('/detect', json={'image': frame()}, headers={'Content-Length': str(main.MAX_BODY + 1)})
        self.assertEqual(result.status_code, 413)
        self.assertEqual(self.client.post('/detect', json={}).status_code, 422)

    def test_cors_preflight(self):
        result = self.client.options('/detect', headers={'Origin': 'http://127.0.0.1:5189', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers['access-control-allow-origin'], 'http://127.0.0.1:5189')

    def test_inference_lock_keeps_health_responsive(self):
        main.detector.local.model = object()
        def slow_test_inference(image):
            sleep(.3)
            return []  # Test fixture, not a production detector.
        main.detector.detect = slow_test_inference
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.client.post, '/detect', json={'image': frame()})
            sleep(.06)
            self.assertEqual(self.client.get('/health').status_code, 200)
            second = self.client.post('/detect', json={'image': frame()})
            self.assertEqual(second.status_code, 429)
            result = first.result()
            self.assertEqual(result.status_code, 200)
            self.assertTrue(result.json()['success'])
            self.assertEqual(result.json()['detections'], [])


if __name__ == '__main__':
    unittest.main()
