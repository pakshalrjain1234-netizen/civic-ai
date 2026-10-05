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
