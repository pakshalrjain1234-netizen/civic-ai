"""Local CivicEye V2 inference; rejected pothole models are never loaded."""
from .detector import CivicDetector
import os

class HybridDetector:
    def __init__(self, root, confidence=.35):
        self.model_path = root / 'models/version-2/civiceye-v2.onnx'
        self.local = CivicDetector(self.model_path, confidence)
        self.accepted = False
        self.warning = ('Automatic pothole detection unavailable. Use Report an issue '
                        'to submit a pothole photo for authority review.')

    @property
    def model(self): return self.local.model

    @property
    def error(self): return self.local.error

    def load(self): self.local.load()

    def health(self):
        gw = self.local.model is not None
        return {'status':'online', 'model_loaded':gw,
            'garbage_waterlogging_detector':gw, 'pothole_detector':False,
            'pothole_runtime':'onnx', 'ready':gw, 'automatic_pothole_ready':False,
            'runtime':'onnx', 'model':'civiceye-v2.onnx',
            'pothole_evaluation':'pretrained and zero-shot candidates failed acceptance',
            'pothole_reporting':'user-assisted',
            'supported_classes':['garbage','waterlogging'],
            'model_error':self.error, 'pothole_error':self.warning,
            'inference_location':'render' if os.getenv('RENDER') else 'local',
            'cloud_inference':bool(os.getenv('RENDER')), 'paid_api_dependency':False}

    def detect(self, image):
        return [{**d,'detector':'civiceye-v2'} for d in self.local.detect(image)
                if d['class'] in ('garbage','waterlogging')]

    def close(self): pass
