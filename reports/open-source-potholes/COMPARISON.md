# CivicEye pothole comparison — 6 October 2026

Training stopped cleanly after epoch 22. No restart or new training. The monitoring follow-up is paused. Existing checkpoints, logs, CSV, config and evaluation scripts have been hash-verified unchanged; backup copies are preserved. V1 and V2 weights and dataset manifest hashes are unchanged. No deployment or paid inference API.

## Sources and practical availability

| Candidate/source | Architecture | License / obligations | PT / ONNX MB | Input/runtime |
|---|---|---|---:|---|
| [Warstad11 camera model](https://github.com/warstad11/pothole) | YOLOv8n / 3.01M params | MIT repository; retain upstream Ultralytics AGPL obligations | 6.25 / 12.24 | 640 x 640, free local CPU |
| [EngJamesO pothole-detector](https://huggingface.co/EngJamesO/pothole-detector) | YOLOv8n / 3.01M params | MIT model card; retain upstream Ultralytics AGPL obligations | 6.25 / 12.24 | 640 x 640, free local CPU |
| [Harisanth Pothole-Finetuned-YOLOv8](https://huggingface.co/Harisanth/Pothole-Finetuned-YOLOv8) | YOLOv8 / 11.14M params (small-sized) | MIT model card; retain upstream Ultralytics AGPL obligations | 22.49 / 44.72 | 640 x 640, free local CPU |
| [dronefreak RDD2022 YOLOv8m](https://huggingface.co/dronefreak/rdd2022-yolov8m) | YOLOv8m / 25.86M params | AGPL-3.0 model card; RDD2022 CC BY-SA 4.0 attribution | 52.03 / 103.60 | 640 x 640, free local CPU |

All four have downloadable PT weights, no upstream ONNX artifact, and were converted locally to static 640 float32 ONNX without training. Source PT files were preserved. Ultralytics/Torch were used only for isolated export; normal inference used ONNX Runtime, no Torch/cloud inference. Publisher license declarations and upstream AGPL obligations are recorded separately. No proprietary relicensing is asserted. [Ultralytics licensing](https://www.ultralytics.com/license).

## Actual CivicEye test results

16 positive images / 28 labeled potholes and 41 backgrounds. Confidence was chosen on validation only (128 images). Precision/recall use one-to-one IoU >= 0.50 matching. AP uses scores down to 0.001, so AP can be nonzero while operating-threshold recall is zero. Mean timing includes letterbox, inference and NMS on Ryzen 3 7320U CPU with two ORT threads; excludes decoding, network and warmup.

| Candidate | Confidence | Precision | Recall | mAP50 | mAP50-95 | Background FP | Mean time | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| warstad | 0.75 | 0.00% | 0.00% | 0.72% | 0.39% | 0/41 (0.00%) | 0.163s | FAIL |
| engjames | 0.25 | 31.58% | 21.43% | 21.14% | 8.64% | 2/41 (4.88%) | 0.165s | FAIL |
| harisanth | 0.35 | 79.41% | 96.43% | 95.64% | 65.87% | 4/41 (9.76%) | 0.837s | PASS |
| dronefreak | 0.75 | 0.00% | 0.00% | 0.71% | 0.32% | 2/41 (4.88%) | 1.020s | FAIL |

## Hard negatives and visual review

33 supplemental images: 15 manhole/drain covers, 10 road backgrounds already in core test, five vehicles and three wet roads. Deduplication by SHA256 leaves 64 unique backgrounds including core test. Supplemental covers include prior train/val images and are diagnostic, not independent held-out data. Per-image author/source/license records remain in existing manifests, cover index and extra-negative-source record. Categories overlap.

| Candidate | FP / 64 unique backgrounds | FP / 15 extra covers | FP / 3 wet roads |
|---|---:|---:|---:|
| warstad | 0/64 (0.00%) | 0/15 | 0/3 |
| engjames | 8/64 (12.50%) | 6/15 | 0/3 |
| harisanth | 7/64 (10.94%) | 3/15 | 0/3 |
| dronefreak | 3/64 (4.69%) | 1/15 | 0/3 |

Core reviewed road images cover clean roads, repairs, cracks, markings, dark patches and vehicles. Extra covers include drainage grills. Strong shadows are sparsely represented. Harisanth visual review covered every test and supplemental image on four readable pages: green ground truth, red real model predictions. It matches 27 of 28 cavities, with residual errors on table/furniture details, manholes and small road/marking details. Other candidates were reviewed on all positive examples: EngJames repeatedly identifies manholes, dronefreak outlines large repair patches, Warstad detects no potholes at the selected threshold.

## Screening decision

**Harisanth is the preferred candidate. Its numeric gate passes at confidence 0.35: recall 96.43%, held-out FPR 9.76%, unique-background diagnostic FPR 10.94%.** It is not activated or deployed: this fulfills the requested comparison-first stage. Candidate ONNX remains separate at `ai-service/models/pothole-research/harisanth/source.onnx`. Automatic potholes remain disabled; V2 garbage/waterlogging is unchanged. Hybrid local integration and live scheduling/regressions are still pending. Its 0.837s CPU latency calls for throttled single-flight sampling, rather than every-frame processing.

Cautions: test positives contain similar views of a few road scenes; these are current CivicEye screening results, not proof of broad generalization. A 64-bit difference-hash audit found no test-vs-other-split distance <= 5, but does not establish independence from upstream training. Harisanth supplies no training-image list; the RDD model explicitly trained on the same source domain. The Harisanth card claims Medium, but actual loaded weights have 11.14M parameters, so the measured small-sized network is reported. Warstad metadata names its sole class `item`; task interpretation was allowed only for research and blocks deployment.

## Requested technical reference

[coding-parrot/pothole-reporter](https://github.com/coding-parrot/pothole-reporter) code has an [MIT license](https://github.com/coding-parrot/pothole-reporter/blob/main/LICENSE). Default OpenAI detection was excluded. Its [local YOLO README](https://github.com/coding-parrot/pothole-reporter/blob/main/ml/yolo/README.md) explicitly says no trained YOLO weights/ONNX have been published; the pinned repository tree has no PT/ONNX checkpoints. Useful reference for grouped splits, provenance and model contracts; not an available pretrained detector. No code was copied into the frontend/backend.

## Other researched alternatives

TamAko783/YOLO26n_RDD_Base: public PT 5.40MB, AGPL card, no ONNX; the newer architecture is unsupported by the isolated 8.3.240 exporter, so not scored. Academic YOLOv8-PD and YOLO-RD papers were research leads, but licensed downloadable weights were not established. They are not claimed as evaluated models.

Previously completed local zero-shot evaluation on the same CivicEye positives: Grounding DINO recall 17.86%, background FPR 61/62 (98.39%); OWL-ViT recall 21.43%, FPR 46/62 (74.19%). These are historical saved measurements, not fresh tests this turn. COCO RT-DETR weights have no pothole class and were not relabeled. Since a new candidate passes numeric screening, no random alternative download cycle was started.

## Audit trail

Pinned source revisions, source/ONNX SHA256, raw genuine predictions, image hashes/timings, validation sweeps and contact sheets are retained per candidate. COMPARISON.json includes preservation proofs; STOPPED_TRAINING.json includes all checkpoint/log backup paths. Scripts: work/research_open_potholes.py, work/download_open_potholes.py, work/export_open_potholes.py, work/evaluate_open_potholes.py. None call training or paid inference.