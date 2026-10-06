# Active local prototype: Harisanth pothole specialist

User approved local integration at confidence 0.35 on 6 October 2026. Active file: pothole.onnx. HARISANTH_ACCEPTANCE.json binds screening acceptance to SHA256; the backend verifies this hash and actual ONNX session loading before marking pothole_detector=true. Separate CivicEye V2 weights handle garbage and waterlogging; V2 pothole scores are excluded.

Source: https://huggingface.co/Harisanth/Pothole-Finetuned-YOLOv8, pinned revision30a4d21de50998dbfa7cc79abb0d7a0d4aa71a4d. Publisher model card declares MIT; upstream Ultralytics AGPL obligations remain. Model card and exact source record are preserved beside this file. No training, paid API, or cloud inference was introduced. Model conversion used isolated Torch/Ultralytics; normal inference is ONNX Runtime.

Integrated 640px JPEG evaluation: recall27/28, core backgroundFP3/41, unique backgroundsFP7/64, manholeFP4/15, mean both-model backend605ms; V2 garbage9/15 and waterlogging19/23 matches unchanged.

Screening: recall27/28; background FP4/41; supplemental cover FP3/15. Manhole/furniture/road-detail false positives remain. Test positives contain similar views and upstream training overlap is unknown. Do not make production/generalization claims.

Photos run both models. Live requests run V2 every sampled frame and request potholes every2seconds, with single-flight requests and no frame/result cache. Same-class overlapping duplicates and almost identical cross-class boxes keep the strongest score. Smaller nested pothole/water regions may coexist. Overlay expiry remains900ms; skipped pothole frames do not erase the temporal confirmation history.

No deployment authorized. Integrated genuine API results and latency are in reports/harisanth-integration. Physical camera/browser verification must not be inferred from unit/ASGI tests.

## Historical rejected candidates (not active)

# Local pothole specialist evaluation

No candidate passed the current CivicEye held-out checks. All three models load
with ONNX Runtime CPU; none is enabled for Live Scan. `LOCAL_ACCEPTANCE.json`
records the rejection. `pothole.onnx` is deliberately absent: copying a failed
candidate into the active path would imply acceptance that did not occur.

Confidence was fixed at 0.35, NMS IoU at 0.45, box matching IoU at 0.50. Each model
was run on all 16 pothole-positive test images (28 boxes), all validation/test
images, and all 408 existing background images: 575 distinct dataset images per
model. A separately licensed and manually reviewed wet-road image was also tested;
it is evaluation-only and was not added to Dataset V2.

| Candidate | Validation recall | Test box recall | Test background FP images | All background FP images |
|---|---:|---:|---:|---:|
| peterhdd YOLOv8s | 4/56 | 2/28 (7.1%) | 4/41 | 48/408 |
| vinothvikas1987 road-distress YOLOv8s, pothole class only | 0/56 | 0/28 | 2/41 | 5/408 |
| khoa-na YOLO26n segmentation detection head | 0/56 | 7/28 (25%) | 32/41 | 368/408 |

Higher image-level detection counts are not recall: predictions on lane paint,
manholes and repaired asphalt failed box matching. Khoa's higher test recall came
with unacceptable background false positives. No threshold was tuned on test data.
The published sources do not establish that their training data never overlapped
CivicEye's RDD images; Vinoth explicitly used RDD. Results are local compatibility
and acceptance checks, not an independent benchmark claim.

## Sources and licenses

- Peter Haddad: https://huggingface.co/peterhdd/pothole-detection-yolov8
  revision `da7747eea7abb4319a0f55961f31809a16c1b10a`.
  Published card Apache-2.0; embedded Ultralytics export metadata AGPL-3.0.
- Vinoth Vikas: https://huggingface.co/vinothvikas1987/pothole-detection-yolov8
  revision `b001687443175e43442f63bef4691c3546629def`.
  Published card Apache-2.0; embedded Ultralytics export metadata AGPL-3.0.
  Only class 3, Pothole, evaluated. Other road-distress classes were excluded.
- Khoa Nguyen: https://github.com/khoa-na/pothole-gps-localization
  revision `80a34b8104e513b596927457347e513f0e0a2ca7`.
  Explicit model AGPL-3.0. LICENSE, model card, third-party notices retained.
  Its two training datasets are described upstream as MIT; preserve attribution.
- Warren Stading: https://github.com/warstad11/pothole
  revision `4e6c793c9c724affb879e5fca63373a4579ba76f`.
  MIT repository reviewed. No published ONNX; camera checkpoint not converted.
  Author reports poor dashcam transfer. This candidate was not evaluated locally.

Do not silently relabel Apache cards as the sole artifact license. Preserve both
publisher declarations and embedded notices; resolve discrepancies before model
redistribution. No paid license or API was purchased or used.

`candidates/` holds unmodified evaluation artifacts. `provenance/FINAL_REPORT.json`
contains their SHA256, timing, class settings, confidence distributions and
overlapping background category counts. `provenance/` retains downloaded source
cards/metadata/notices. Historical OPENAI_ACCEPTANCE records describe a removed
route and do not activate anything. No credential is required or retained by the
current local inference configuration.
