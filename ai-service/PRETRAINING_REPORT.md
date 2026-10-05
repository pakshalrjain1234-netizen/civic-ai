> SUPERSEDED for current counts/training status by COLAB_PREPARATION_REPORT.md and ../../CivicEye_Colab_Guide.md. The following records historical preparation.

# CivicEye final background preparation and training status

Added **100 real negative images**, split **70 train / 20 validation / 10 test**, each with an empty YOLO label file. The existing 814 real positive images (275 pothole, 339 garbage, 200 waterlogging) and 203 selected synthetic images are unchanged. **1,117 active images total**; the original 397 synthetic images remain preserved separately. 26 selected synthetic images are background, included in the 203.

| Split | Total images | Real positives | Real negatives | Synthetic | Real pothole positives | Real garbage positives | Real waterlogging positives |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 857 | 584 | 70 | 203 | 200 | 244 | 140 |
| val | 175 | 155 | 20 | 0 | 50 | 65 | 40 |
| test | 85 | 75 | 10 | 0 | 25 | 30 | 20 |

## Validation and manual review

All 1,117 images and label files pass corruption, missing/orphan label, exact hash, class-ID and normalized-box checks. Near-duplicate screening found 3 candidate pairs, all within the same split; zero across splits. Countries, TACO batches and known waterlogging scene groups remain intact. Perceptual hashes cannot certify all possible scene relationships. Validation and test contain only real images.

Object boxes (real + synthetic): train 491 pothole / 940 garbage / 271 waterlogging; validation 60 / 203 / 54; test 37 / 88 / 23. Total 588 / 1,231 / 348. Garbage boxes remain substantially more numerous, so per-class evaluation is essential. Negatives do not receive a fourth class.

All 165 candidate negative thumbnails reviewed: 110 India, 35 Czech, 20 China motorbike. India/Czech source XML has no objects; China has no D40 and may contain unrelated cracks. Excluded ambiguous damage/material and redundant views; selected one representative per perceptual candidate pair among negatives. No images were duplicated to reach 100. Hard negatives include shadows, patches, repairs, markings, covers and dusty roads. No safely cleared reflective wet-road or harmless puddle negatives were added. Original candidate XML and explicit selection/exclusion manifest are retained under data-sources/background/RDD2022.

Contact sheets use deterministic random samples of up to 8 real images per class per split, with original YOLO boxes drawn red pothole / green garbage / cyan waterlogging. Negative sheets have no boxes. See dataset/review/*-sample.jpg and visual-review-notes.json.

**Visual review is not an unconditional pass:** original RDD D40 includes some cracks/repaired-seam-looking positives, notably rdd_5b5829b4028e1798ba84.jpg in test. This conflicts with the intended repaired-asphalt background definition and needs adjudication before declaring labels semantically clean. TACO labels individual litter, including small/staged examples, broader than garbage piles. Waterlogging component rectangles are enclosing boxes, not exact water boundaries. Positive labels/counts were preserved. These concerns are explicit rather than hidden by valid-file checks.

## Licenses and attribution

RDD positive and negative derivatives retain **CC BY-SA 4.0**, following the original author repository image notice. Official Figshare metadata says CC BY 4.0; the discrepancy is preserved, not silently resolved. All original creators, source/license links and modifications retained in licenses/ATTRIBUTION.md and RDD2022-license-verification.json.

TACO published release: **CC BY 4.0** (toolkit MIT separate). Image Dataset for Roadway Flooding: **CC BY 4.0**, Cem Sazara, Mecit Cetin, Khan Iftekharuddin (2019), DOI 10.17632/t395bwcvbw.1. IRDID, FloodNet and FRED are not imported. Synthetic assets remain user supplied, with external redistribution rights not independently verified.

## Training did not start

User approved first prototype training conditional on successful validation. Hardware/runtime preflight failed: **Windows Application Control blocked torch/lib/torch.dll or a dependency, WinError 4551**. Installed scratch runtime: PyTorch 2.14.1, Ultralytics 8.4.171. No protection was disabled or bypassed. Eight logical CPU threads detected; GPU availability and training speed could not be measured because PyTorch cannot initialize. No claim that GPU or CPU training was performed.

Training duration **0 seconds**, epochs **0**. Per-class precision, recall, mAP50, mAP50–95 and confusion matrix are **unavailable** because there is no trained model. No accuracy numbers or detections have been fabricated. training/validate.py now exports all four metrics per class plus a confusion matrix when run with real weights.

Required checkpoint path after actual training: `training/runs/civiceye/weights/best.pt`. Deployment target: `models/civiceye.pt`. **Neither exists.** No service restart for new weights was attempted because no new model exists. Existing FastAPI /health is online with model_loaded false; the actual Live Scan page reads AI SERVICE CONNECTED — MODEL NOT LOADED and AI model: model required. **Live Scan is not ready for real model testing.** Frontend and Live Scan code were not altered.

## Resume in an approved training environment

Resolve the recorded D40 semantic ambiguities, then install ai-service/requirements.txt in an approved Python environment. From ai-service, use the existing tools:

```powershell
python training/train.py --check-only
python training/train.py --pretrained yolo11n.pt --epochs 50 --imgsz 640 --batch 8 --device 0 --no-deploy
python training/validate.py --weights training/runs/civiceye/weights/best.pt --split val --device 0 --name civiceye-val
python training/validate.py --weights training/runs/civiceye/weights/best.pt --split test --device 0 --name civiceye-test
```

Use device cpu only when CUDA is unavailable; 50 epochs at 640 on a laptop CPU may take hours, so establish the first epoch timing before committing to a schedule. Review real per-class metrics, confusion matrices, false positives and predictions before copying best.pt to models/civiceye.pt. Restart FastAPI only after copying the validated checkpoint and verify /health plus Live Scan. Do not overwrite an earlier trained run or checkpoint without preserving it.
