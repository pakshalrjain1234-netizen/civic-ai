> SUPERSEDED for current counts/training status by COLAB_PREPARATION_REPORT.md and ../../CivicEye_Colab_Guide.md. The following records historical preparation.

# CivicEye dataset sources — verified 2026-10-02

| Dataset | Used real photos | Source class → CivicEye | Verified original license/status |
|---|---:|---|---|
| RDD2022 | 275 (India 200, Czech 50, China MotorBike 25) | D40 → 0 pothole | Original author image notice **CC BY-SA 4.0**; Figshare CC BY 4.0 conflict preserved, ShareAlike retained |
| TACO published release | 339 | Annotated litter → 1 garbage | **CC BY 4.0**, official Zenodo release |
| Image Dataset for Roadway Flooding | 200 | Binary road-water mask 1 → 2 waterlogging | **CC BY 4.0**, original Mendeley release |
| IRDID | 0 | Only waterlogged road / optional pothole would be eligible | Repository CC BY 4.0; original photo rights and detection annotations unresolved |
| FloodNet | 0 | Road-flooded mask 3 → 2, supplementary training only | **CDLA Permissive 1.0** |
| FRED | 0 | Street-level road-water annotations | Official metadata **CC BY-NC-SA 4.0**, gated downloads |
| Physical demonstration | 0 | Team-annotated 0/1/2 | Team-owned authorized recordings, not yet supplied |
| User starter | 0 real; 397 synthetic retained, 203 used | Synthetic 0/1/2 | User supplied; external redistribution rights not independently verified |

RDD original source: https://github.com/sekilab/RoadDamageDetector#license ; release: https://figshare.com/articles/dataset/21431547 . Original README specifies CC BY-SA 4.0 for images; Figshare metadata says CC BY 4.0. Do not erase that discrepancy or confuse the repository's MIT software license with its image notice. CivicEye retains the original ShareAlike and attribution obligations for derived RDD images/annotations. Evidence and all release creators are in licenses/RDD2022-license-verification.json and ATTRIBUTION.md. Bounded nested-ZIP byte ranges fetched the subsets without downloading the 13 GB release. Only D40 boxes are mapped; unrelated cracks are omitted. Whole countries remain intact for splitting.

TACO: https://zenodo.org/records/3587843 , Pedro F. Proença and Pedro Simões, TACO (2020). Dataset license CC BY 4.0, independently from toolkit MIT. Release-provided 640-size photo URLs and scaled COCO boxes; 200 + 171 retained, 32 hash overlaps removed, 339 unique photos. Two subpixel edge corrections documented. Individual litter is broader than garbage piles; collector batches stay together and local phone/accumulation scenes should supplement the prototype.

Street-level waterlogging: original authors Cem Sazara, Mecit Cetin, Khan Iftekharuddin, Old Dominion University (2019), **Image Dataset for Roadway Flooding**, DOI 10.17632/t395bwcvbw.1, https://data.mendeley.com/datasets/t395bwcvbw/1 . CC BY 4.0. Direct official archive succeeded (16.8 MB; 441 image/mask pairs). Reviewed all image thumbnails, removed aerial/non-road/ambiguous views and known repeated-scene candidates, selected 200 street-level examples. Original indexed mask 1 floodwater is converted to 8-connected-component rectangles of at least 500 pixels, then YOLO class 2. Masks, selection and conversion notices retained. Boxes still require final full-size approval. Street-level waterlogging split: 140 train / 40 val / 20 test. No images were duplicated to increase counts.

IRDID: https://github.com/ahs695/Indian-Road-Damage-Infrastructure-Dataset . Pinned repository/LICENSE/metadata audit only; zero photographs imported. Declared CC BY 4.0 cannot resolve the generic Google creative commons photo origins. 200 water filenames correspond to 96 unique Git blobs. Classification CSV has no boxes. Optional pothole metadata names newspaper sources. Do not use source random splits or invent bounding boxes. See licenses/IRDID/audit.json.

FloodNet: https://github.com/BinaLab/FloodNet-Supervised_v1.0 , CDLA Permissive 1.0, Rahnemoonfar et al. (2021), DOI 10.1109/ACCESS.2021.3090981. No relevant exposed initial-mask pairs imported. **Aerial supplement only**, capped at 20% of external real waterlogging images and excluded from validation/test. Future conversion uses mask 3 road flooded; water/pool/building classes are omitted.

FRED: https://huggingface.co/datasets/CMalone-Jupiter/FRED , author-linked by https://arxiv.org/abs/2605.22018 and AVR3 SDK. CC BY-NC-SA 4.0; public metadata accessible, gated file/card retrieval returned HTTP 401. Zero imported, no bypass attempted. It is not required now because the licensed original Roadway Flooding subset was acquired.

See DATASET_REPORT.md, dataset/class_balance.json and licenses/ATTRIBUTION.md for current balance, modifications and credits. All real classes occur in all splits. No model was trained. First prototype training is now conditionally authorized by the user, but blocked by PyTorch Application Control and recorded label semantics concerns; see PRETRAINING_REPORT.md. The mixed sources retain their own licenses and do not imply endorsement or production accuracy.

## Added real backgrounds
100 reviewed RDD2022 negative photos, India 70 train / Czech 20 val / China MotorBike 10 test. Source XML contains no objects for India/Czech and no D40 for China; manually screened for garbage, potholes and meaningful waterlogging. Empty YOLO labels are reviewed negatives, not missing annotations. Original image license/ShareAlike conflict remains preserved. Attribution and modifications recorded in licenses/RDD2022-background-import.json. Current active data: 814 real positives + 100 real negatives + 203 synthetic = 1,117.
