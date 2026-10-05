# CivicEye local vision and assisted pothole reporting

The existing localhost `POST /detect` runs the unchanged V2 ONNX model for garbage
and waterlogging. Its pothole output is filtered. V1 and V2 weights are preserved.
Normal inference uses ONNX Runtime CPU and makes no network call or torch import.
No paid model API, key or billing is required. Local mode processes frames on
the device; the optional user-approved Render deployment processes frames on
your own free hosted ONNX service, which is truthfully reported by /health.

All three earlier pothole-specific candidates were rejected. The requested
Grounding DINO and OWL-ViT local quantized zero-shot models were subsequently tested
and also rejected. See [the zero-shot review](ai-service/models/pothole-zero-shot/README.md).
Their raw predictions, all prompt/threshold results, licenses and hashes are stored
under `ai-service/models/pothole-zero-shot/`. The service does not load any rejected
artifact. No training, model modification or Dataset V2 changes occurred.

## Current truthful readiness

`/health` reports status online, model_loaded true and
garbage_waterlogging_detector true after actual V2 loading succeeds. It reports
pothole_detector false and pothole_reporting user-assisted. ready now indicates
readiness of the supported garbage/waterlogging service; automatic_pothole_ready
remains false. Render preparation is documented in DEPLOYMENT.md. Live Scan
keeps its existing layout and reflects partial readiness. No heavy specialist
scheduler or automatic pothole inference was enabled because none passed.

## User-assisted potholes

In the local citizen prototype, capture/upload a photo in Report an issue and choose
"Report this photo as a pothole". The citizen supplies a severity estimate and
confirms the coordinates. The report records user-assisted provenance, null AI
confidence and Review Required status. Normal priority, Road Maintenance routing,
authority review and worker assignment continue to work.

The analysis/review/detail views explicitly distinguish citizen reports from AI
detections. Manual before/after evidence cannot automatically verify a repair;
authority must review it. Browser-local records and evidence persist across role
changes. Test incident CIV-8986B3D8 is explicitly labeled as an automated workflow
test, not a real complaint. Its authority review, assignment and worker visibility
were verified through the existing UI.

The old Supabase image-analysis function returns HTTP 410; browser image analysis
uses the local service. Shared production submission requires a trusted reporting
bridge and is not claimed as implemented. Local demonstration roles are not
production authentication.

## Startup

From `ai-service`, use a Python environment with `requirements.txt` installed:

```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

The existing frontend remains at http://127.0.0.1:5189/. No Colab or API credential
is required for these current local inference and assisted-reporting paths.
