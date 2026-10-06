# Moving-camera scan update

The existing Live Scan layout, /detect JSON contract and V2 weights are preserved.
Capture uses a longest dimension of 640 px with JPEG quality 0.8. The attempted
0.70 setting lost two matched waterlogging boxes and was rejected; 0.75 also lost
one. The retained setting preserves matched detections across all 92 held-out V2
test images. These JPEG size measurements use Pillow encoding as a repeatable
proxy; a physical Android browser's encoder/network can differ. Browser capture
records actual JPEG bytes and round-trip time in scan.captureMetrics/requestMetrics.

Each cycle captures three frames 80 ms apart, scores Laplacian variance on a tiny
thumbnail and uploads only the sharpest. Canvas contexts are reused. Scan starts
are approximately 300 ms apart when requests are quick, with at least an 80 ms gap
after a slow request and a 1 s error backoff. Capture plus inference remains a
single flight. Pausing, stopping, changing mode and going offline clear history;
late responses cannot repopulate a paused/stopped scan.

Detections at confidence >=0.65 appear immediately. Other existing valid model
detections require matching class and overlap in an adjacent response within
1.2 s. This does not reduce backend confidence (0.35) or NMS (0.45). A confirmed
overlay can remain for 900 ms after its last valid result; missed-frame overlays
fade and are labeled recent. Expiry also runs while inference is pending. Only
fresh confirmed detections save real frames in the findings feed; incidents
still require the user's explicit action.

Backend debug profiling is enabled only with CIVICEYE_DEBUG_TIMINGS=1. It reports
decode, preprocessing, ONNX inference, postprocessing and endpoint processing
time. The existing inference lock and one Uvicorn worker are retained. Sequential
CPU execution, full graph optimization and a bounded 1–4 intra-op thread option
are explicit. Default remains two threads: local 4-thread gains do not represent
Render Free's CPU quota. Reference:
https://onnxruntime.ai/docs/performance/tune-performance/threading.html

Results and prediction contact sheets: reports/moving-scan/.
No physical moving-phone/mobile Live Scan test was available. Controlled scan
tests verify frame selection, temporal behavior, cancellation and single flight;
they do not prove walking-camera performance. The current hosted backend's compute
time alone was roughly 0.84–1.24 s. Sub-second production response is not achieved
or promised by these measurements. New code has not been deployed.

## Pothole specialist preparation

Separate corpus: ai-service/dataset-pothole-specialist. Approved V2 is untouched.
300 original real pothole images; 611 annotated boxes, 393 below 1% of image area.
Median original box area is 0.61%; contextual training crops raise median crop
box area to 2.62%. This supports a small-object/domain explanation, not proof of
the earlier model's sole failure cause. Inherited road-view labels can be
ambiguous patches/cracks; close-range phone photos remain a coverage gap.

Training: 238 original positives + 506 derivatives + 285 original negatives
(1029 images). Validation: 46 original positives + 82 negatives (128). Test:
16 original positives + 41 negatives (57). Validation/test are uncropped.
Parent groups and original near-duplicate groups stay within their splits.
93,610 derivative/held-out comparisons flagged no perceptual near-duplicate
candidates. This is a conservative heuristic, not proof of universal scene
independence. Image and label checks pass; crop contact sheet was visually checked.
Source/license records are retained, including derivative parent provenance.

Local preparation/training/independent ONNX evaluation entry points are in
ai-service/training/*pothole_specialist.py. YOLO11 Nano foundation weights and
their original source/hash/license are in training/pretrained. Training settings
for the current run are 60 maximum epochs, patience 15, 640 input, batch 8 on CPU;
768 is optional. CPU training requires an explicit --allow-cpu argument because
it can take many hours. A working isolated PyTorch 2.6 CPU runtime was prepared
and the real training job started. Neither training nor evaluation activates a candidate.

Independent ONNX acceptance checks matched boxes at IoU >=0.5 and false-positive
negative-image rate. Targets: recall >=60%, negative false-positive rate <=15%.
Validation is available for configuration selection; original test scenes remain
the final gate. Numeric success is insufficient: predictions must also be
reviewed. No accepted pothole weights exist from this update and automatic
potholes remain disabled. V1/V2 ONNX files are unchanged. No paid inference API
or OpenAI key is used in the active detection path.
