> SUPERSEDED by PRETRAINING_REPORT.md for current counts and training authorization/status. The following is historical waterlogging preparation.

# CivicEye waterlogging preparation report — 2026-10-02

**No training was run. Frontend and Live Scan were not changed.** The external dataset now has real street-level waterlogging and all three classes in every split. It is ready for final dataset review and user approval for first prototype YOLO training, not yet approved for training. This is not a real-world accuracy result.

## IRDID outcome

Repository/license/annotation metadata downloaded successfully, pinned to commit 98b12608720a2903878176598a3c94cf4d5561b6. **Zero IRDID training photographs downloaded or imported.** Its declared repository license is CC BY 4.0, but water photo provenance is only “Google creative commons” without original URL/creator/exact license; optional pothole data credits newspapers. Its 200 waterlogging filenames represent **96 unique Git image blobs and 104 duplicate copies**. Its CSV labels contain image,label only, not localization boxes. These are concrete reasons it cannot supply 200 cleared detection examples. Evidence: licenses/IRDID/audit.json, tree.json, LICENSE and original metadata CSV.

## Successfully imported alternative

**200 unique real street-level waterlogging images** from Image Dataset for Roadway Flooding, original authors Cem Sazara, Mecit Cetin and Khan Iftekharuddin, Old Dominion University (2019), DOI 10.17632/t395bwcvbw.1. Original Mendeley release: https://data.mendeley.com/datasets/t395bwcvbw/1 , **CC BY 4.0**.

Direct original-author archive download succeeded (16.8 MB, 441 paired images/masks). All 441 image thumbnails were reviewed; 349 were eligible street-level road scenes. Non-road, aerial, vehicle-only and ambiguous views were excluded. Three visual-hash candidate pairs plus 23 manual repeated-scene lists reduced eligible candidates to 324 clusters; selected at most one representative per cluster, then a seeded sample of 200. Selection/audit files preserve IDs and exclusion reasons/method; no artificial image duplication or augmentation was used to reach 200 real images.

Segmentation conversion: original grayscale masks are indexed **0 background / 1 floodwater**. Each 8-connected foreground region with at least 500 pixels yields its enclosing rectangle, normalized to the image size as **YOLO class 2 waterlogging**. Original masks are retained. Irregular water regions can yield loose or fragmented rectangles, so full-size box review and user approval remain required. No image-wide boxes were fabricated from classification labels.

**FloodNet imported count: 0.** It remains optional aerial-domain supplementation, training only, capped at 20% of external real waterlogging images. Street-level waterlogging is the main source and the only waterlogging source in real validation/test. Physical-demo folders and frame extraction/import tools remain ready; no phone recordings were required for this preparation.

## Current active dataset

**1,017 images: 814 real + 203 synthetic** (80.0% real / 20.0% synthetic). The complete original 397-image synthetic starter remains preserved separately; only 203 are selected as training augmentation. Real class-positive photo counts: **275 pothole / 339 garbage / 200 waterlogging**. Individual images containing multiple synthetic classes count positively toward each applicable class.

| Split | Real images | Synthetic images | Real pothole images | Real garbage images | Real waterlogging images | Pothole boxes (all) | Garbage boxes (all) | Waterlogging boxes (all) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TRAIN | 584 | 203 | 200 | 244 | 140 | 491 | 940 | 271 |
| VALIDATION | 155 | 0 | 50 | 65 | 40 | 60 | 203 | 54 |
| TEST | 75 | 0 | 25 | 30 | 20 | 37 | 88 | 23 |

Real box counts by split: pothole **422 / 60 / 37**, garbage **869 / 203 / 88**, waterlogging **203 / 54 / 23**. Synthetic train boxes: pothole **69**, garbage **71**, waterlogging **68**; validation/test contain no synthetic images or boxes. There are 26 reviewed synthetic backgrounds and no real background-only images yet.

Real split ratio: **71.7% train / 19.0% validation / 9.2% test**; small deviation from 70/20/10 keeps acquisition groups intact. India potholes (200) stay in train, Czech potholes (50) stay in validation, and China MotorBike potholes (25) stay in test. The 75 extra real pothole images were downloaded as bounded official RDD subsets to provide independent held-out countries; no country/unknown road sequence was randomly split. TACO batches remain together. Reviewed waterlogging scene candidates remain intact, with 140 / 40 / 20 street-level images.

## License verification and attribution

- **RDD original image notice: CC BY-SA 4.0**, https://github.com/sekilab/RoadDamageDetector#license . Official RDD2022 Figshare metadata instead says CC BY 4.0. Both records remain preserved. CivicEye retains attribution, modification notices and ShareAlike on RDD image/annotation derivatives rather than silently discarding the original obligations; definitive reconciliation of the conflicting release notices would require the authors. All release creators and changes are listed in licenses/ATTRIBUTION.md. No blanket CC BY license is applied to the mixed dataset.
- **TACO published-release dataset: CC BY 4.0**, https://zenodo.org/records/3587843 . Authors, provided lower-resolution photo retrieval and label scaling/deduplication are recorded.
- **Roadway Flooding original release: CC BY 4.0**, https://data.mendeley.com/datasets/t395bwcvbw/1 . Dataset author/source/license and mask-to-box modifications are recorded.
- **FloodNet: CDLA Permissive 1.0**, https://github.com/BinaLab/FloodNet-Supervised_v1.0 ; not imported.
- **IRDID: repository declares CC BY 4.0; underlying photo rights unresolved**, not imported.
- **FRED: CC BY-NC-SA 4.0** on the official author-linked dataset metadata; gated HTTP 401 download, not imported. No credentials/access-control bypass attempted.
- Synthetic: user supplied, external redistribution rights not independently verified. Physical-demo: no recordings yet.

## Validation, imbalance and readiness

All active images/labels passed the missing-file, image-corruption, class-ID, normalized-box, duplicate-filename, exact-hash and orphan-label checks. All three classes have real positive examples in every split. Visual hash screening found **3 near-duplicate candidate pairs, zero across splits**; known/manual related scenes are not divided. Perceptual hashes are a screening tool, not proof of perfect independence or all possible crops/sequence matches.

Image counts have a modest imbalance (275/339/200). **Object-box imbalance is larger:** real boxes 519 pothole, 1,160 garbage, 280 waterlogging. Evaluate per-class precision/recall/mAP after approved training rather than presenting one aggregate score. Collect real clean-road negatives and local phone-view/physical-demo frames when available to assess false positives/domain shift; the current prototype does not establish production or demo-tray accuracy.

**Ready for dataset review and first prototype training after approval:** yes, file/class/domain coverage preflight passes. **Approved or trained:** no. Review the retained masks and boxes, source/ShareAlike records, and scene candidates before approving. Keep validation/test untouched during later training decisions.

## Files created or updated

Created: licenses/RDD2022-license-verification.json, ATTRIBUTION.md, IRDID audit/metadata/license evidence, RoadwayFlooding license/download/selection records, Czech/China RDD download logs; scripts/check_near_duplicates.py and dataset_balance.py; dataset/class_balance.json, near_duplicate_report.json and reviewed waterlogging contact sheets. Added converted class-2 street-level examples and 75 held-out-country pothole photos.

Updated: DATASET_SOURCES.md, REAL_DATA_DOWNLOAD_GUIDE.md, license README/records, scripts/import_real_dataset.py (binary road-water conversion, class-aware intact-group allocation, aerial limit), download_open_subset.py (original-license verification and bounded country selection), dataset manifests/stats/READINESS.json, README descriptions and source ZIP. Physical-demo is ready and empty. Historical dataset backups remain outside the source ZIP; no frontend, Live Scan, inference code or model weights changed.
