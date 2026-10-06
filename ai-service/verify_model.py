"""Check that the approved V2 file survived repository/package transfer unchanged."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
record = json.loads((root / 'models/version-2/deployment-model.json').read_text())
model = root / record['path']
if not model.is_file():
    raise SystemExit(f'Approved model is missing: {model}')
actual = hashlib.sha256(model.read_bytes()).hexdigest()
if actual != record['sha256']:
    raise SystemExit('Approved V2 model checksum mismatch. Do not deploy a modified model.')
print(f'Approved V2 model verified: {model.name}')

# Fail the build if the accepted specialist is absent, modified, or unloadable.
from utils.pothole_onnx import PotholeDetector
acceptance = json.loads((root / 'models/pothole-specialist/HARISANTH_ACCEPTANCE.json').read_text())
specialist = root / 'models/pothole-specialist/pothole.onnx'
if not acceptance['accepted'] or acceptance['confidence'] != .35 or hashlib.sha256(specialist.read_bytes()).hexdigest() != acceptance['sha256']:
    raise SystemExit('Accepted pothole specialist checksum/configuration mismatch.')
detector = PotholeDetector(specialist, confidence=.35)
detector.load()
if detector.model is None:
    raise SystemExit(detector.error)
print('Accepted Harisanth ONNX specialist verified and loaded.')
