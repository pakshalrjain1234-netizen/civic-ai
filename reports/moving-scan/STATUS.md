# CivicEye update status

Implemented and tested locally; not deployed to Netlify/Render.

Capture JPEG benchmark: 92527 -> 57286 bytes (38% smaller).
Local decode/inference: 114.05 -> 109.85 ms.
Live current Render round-trip: 2019 -> 1419 ms with the new capture size only (6 real images/setting, not randomized; new backend code is not deployed).
Backend computation varied rather than improving: 930 -> 1025 ms. No sub-second production claim.

Garbage matched-box recall unchanged at 9/15 (60%); precision 69.2% -> 75%.
Waterlogging matched-box recall unchanged at 19/23 (82.6%), precision 100%.
Background false-positive images 3/41 -> 2/41. Confidence/NMS unchanged.
All 92 original held-out V2 images were tested. Smaller quality .7/.75 variants were rejected.
These JPEG bytes are measured with Pillow as a repeatable proxy; browser encoding may differ.
Browser single-flight, burst selection, persistence, temporal confirmation and late-response tests pass.
Physical moving-phone test unavailable; real Android performance is not claimed.

Uploaded-photo reporting now uses explicit real AI provenance and hides irrelevant pothole controls after garbage/waterlogging detections. Manual potholes require explicit selection. An old request or scan result cannot overwrite a replacement photo. Simulated findings remain explicitly labeled DEMO — NO AI ANALYSIS. Tests use saved actual production /detect responses.

Pothole training is now possible in a fresh isolated CPU PyTorch 2.6 environment.
Real 60-epoch maximum training was started, patience 15, 640 input, batch 8.
Synthetic-tensor forward/backward benchmark estimated ~14 min/epoch (~14 h maximum); real timing can differ. No GPU. Training is not complete and no acceptance metrics are available.
The production pothole detector remains disabled. No failed pretrained candidate is reused.
Separate specialist corpus: 300 original real positives + 506 training-only crops + 408 negatives.
Train 1029, validation 128, test 57. Validation/test originals uncropped. No flagged pairs in 93610 derivative/held-out perceptual comparisons. Original approved V2 remains unchanged.

Live production /health verified: online, model_loaded=true, garbage_waterlogging_detector=true, pothole_detector=false, ready=true, paid_api_dependency=false.
No new backend/Netlify deployment occurred. GitHub connector exposes no repositories; the existing repository URL and access are still missing.
Render config and V1/V2 model hashes are preserved. No paid inference API was added.

Detailed JSON and comparison sheets are in reports/moving-scan. Training status/logs/results remain in the workspace, excluded from the deployable runtime bundle.
