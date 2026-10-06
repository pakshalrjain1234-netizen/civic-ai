"""Separate accepted local ONNX specialists; no frame/result cache."""
import hashlib
import json
import os
from time import perf_counter
from .detector import CivicDetector
from .pothole_onnx import PotholeDetector


def box_iou(a, b):
    a, b = a['bbox'], b['bbox']
    intersection = max(0, min(a['x']+a['width'], b['x']+b['width'])-max(a['x'], b['x'])) * max(0, min(a['y']+a['height'], b['y']+b['height'])-max(a['y'], b['y']))
    return intersection / max(1e-9, a['width']*a['height']+b['width']*b['height']-intersection)


def merge_detections(detections):
    kept = []
    for detection in sorted(detections, key=lambda d: -d['confidence']):
        if not any(box_iou(detection, previous) >= (.45 if detection['class'] == previous['class'] else .85) for previous in kept):
            kept.append(detection)
    return kept


class HybridDetector:
    def __init__(self, root, confidence=.35):
        self.model_path = root / 'models/version-2/civiceye-v2.onnx'
        self.local = CivicDetector(self.model_path, confidence)
        self.pothole = PotholeDetector(root / 'models/pothole-specialist/pothole.onnx', confidence=.35)
        self.acceptance_path = root / 'models/pothole-specialist/HARISANTH_ACCEPTANCE.json'
        self.accepted = False
        self.warning = None

    @property
    def model(self): return self.local.model

    @property
    def error(self): return self.local.error

    def load(self):
        self.local.load()
        self.accepted = False
        self.pothole.model = None
        try:
            record = json.loads(self.acceptance_path.read_text())
            with self.pothole.model_path.open('rb') as source:
                digest = hashlib.file_digest(source, 'sha256').hexdigest()
            if not record['accepted'] or record['confidence'] != .35 or record['sha256'] != digest:
                raise ValueError('Pothole acceptance record mismatch.')
            self.pothole.load()
            self.accepted = self.pothole.model is not None
        except (OSError, ValueError, KeyError):
            self.pothole.error = 'Accepted pothole specialist missing or hash verification failed.'
        self.warning = None if self.accepted else 'Automatic pothole detection unavailable. Use manual pothole reporting.'

    def health(self):
        gw = self.local.model is not None
        pothole = self.accepted and self.pothole.model is not None
        return {'status':'online', 'model_loaded':gw, 'garbage_waterlogging_detector':gw,
            'pothole_detector':pothole, 'pothole_runtime':'onnx', 'ready':gw,
            'automatic_pothole_ready':pothole, 'runtime':'onnx', 'model':'civiceye-v2.onnx',
            'pothole_model':'Harisanth/pothole.onnx' if pothole else None,
            'pothole_confidence':.35, 'pothole_evaluation':'prototype screening passed; manhole false positives remain',
            'pothole_reporting':'automatic and user-assisted' if pothole else 'user-assisted',
            'supported_classes':(['pothole'] if pothole else [])+['garbage','waterlogging'],
            'model_error':self.error, 'pothole_error':self.pothole.error,
            'pothole_limitations':'Manhole false positives: screening 3/15; integrated 640px JPEG 4/15; limited test scene diversity and unknown upstream training overlap.',
            'live_pothole_interval_ms':2000,
            'inference_location':'render' if os.getenv('RENDER') else 'local',
            'cloud_inference':bool(os.getenv('RENDER')), 'paid_api_dependency':False}

    def detect(self, image, include_pothole=True):
        return self.detect_profiled(image, include_pothole)[0]

    def detect_profiled(self, image, include_pothole=True):
        started = perf_counter()
        detections, timings = self.local.detect_profiled(image)
        detections = [{**d,'detector':'civiceye-v2'} for d in detections if d['class'] in ('garbage','waterlogging')]
        specialist_start = perf_counter()
        if include_pothole and self.accepted and self.pothole.model is not None:
            detections.extend(self.pothole.detect(image))
        timings.update(pothole_ms=round((perf_counter()-specialist_start)*1000,2), hybrid_ms=round((perf_counter()-started)*1000,2))
        return merge_detections(detections), timings

    def close(self): pass
