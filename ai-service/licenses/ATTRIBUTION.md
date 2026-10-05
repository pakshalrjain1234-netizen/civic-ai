# Dataset attribution and modifications

## RDD2022
Title: RDD2022 — The multi-national Road Damage Dataset released through CRDDC 2022.
Creators listed in official release metadata: Deeksha Arya, Hiroya Maeda, Yoshihide Sekimoto, Hiroshi Omata, Sanjay Kumar Ghosh, Durga Toshniwal, Madhavendra Sharma, Van Vung Pham, Jingtao Zhong, Muneer Al-Hammadi, Mamoona Birkhez Shami, Du Nguyen, Hanglin Cheng, Jing Zhang, Alex Klein-Paste, Helge Mork, Frank Lindseth, Toshikazu Seto, Alexander Mraz, Takehiro Kashiyama.
Original source: https://github.com/sekilab/RoadDamageDetector ; official release: https://doi.org/10.6084/m9.figshare.21431547.v1 .
Original author repository image license: **CC BY-SA 4.0**, https://creativecommons.org/licenses/by-sa/4.0/ . The Figshare metadata says CC BY 4.0; both evidence records are preserved. CivicEye retains the original ShareAlike obligations instead of claiming unrestricted CC BY reuse. RDD image/annotation derivatives retain CC BY-SA 4.0 upon redistribution, without changing the licenses of independent TACO/user assets or claiming this notice licenses application code or model weights.
Modifications: selected 200 India photos containing D40, omitted unrelated crack boxes, converted Pascal VOC coordinates to normalized YOLO class 0, renamed by image hash, kept country together to prevent unidentified sequence leakage. No endorsement is implied.

## TACO
Pedro F. Proença and Pedro Simões. TACO: Trash Annotations in Context for Litter Detection (2020).
Verified published-release dataset record: https://zenodo.org/records/3587843 . **CC BY 4.0**, https://creativecommons.org/licenses/by/4.0/ .
Modifications: selected two bounded samples, retrieved release-provided 640-size photo URLs, scaled COCO boxes, mapped litter categories to CivicEye class 1, deduplicated exact images, documented two subpixel edge corrections, retained batches together. Toolkit MIT license is separate.

## FloodNet — not imported
Rahnemoonfar, Chowdhury, Sarkar, Varshney, Yari and Murphy. FloodNet (2021), DOI 10.1109/ACCESS.2021.3090981.
https://github.com/BinaLab/FloodNet-Supervised_v1.0 ; **CDLA Permissive 1.0**, https://cdla.io/permissive-1-0/ . Future mask conversion would derive boxes only from road-flooded mask ID 3. Aerial-domain supplemental training only; prefer real street-level held-out data.

## IRDID — under review, no training images imported
Indian Road Damage & Infrastructure Dataset Contributors (2026), maintained by ahs695.
https://github.com/ahs695/Indian-Road-Damage-Infrastructure-Dataset . Repository declares **CC BY 4.0**. Original photo rights have not been established from its generic Google-creative-commons source field; newspaper-origin pothole images are also not imported. No real count is inferred from filenames or a classification-only label file.

## User synthetic and physical-demo assets
397 synthetic starter images are user-supplied; external redistribution rights not independently verified. Physical demonstration recordings have not yet been supplied. Keep their provenance separate from external datasets.

## Image Dataset for Roadway Flooding
Cem Sazara, Mecit Cetin and Khan Iftekharuddin, Old Dominion University (2019), version 1, DOI 10.17632/t395bwcvbw.1. Original source: https://data.mendeley.com/datasets/t395bwcvbw/1 . CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ .
Modifications: reviewed all 441 image thumbnails, selected 200 street-level road-water scenes, excluded non-road/aerial/ambiguous views, chose one photo per repeated-scene candidate cluster, converted binary masks (foreground 1) to connected-component enclosing YOLO rectangles for CivicEye class 2, minimum 500 foreground pixels. Preserved image/mask pairs and scene-selection records. Images renamed by content hash; scene groups kept intact. No endorsement is implied.

## RDD2022 background subset modification
100 manually screened road-background images, selected from original RDD2022 country archives via bounded official Figshare ZIP ranges. India/Czech zero annotated damage, China no D40 (non-target cracks omitted). Negative label files are explicitly empty after review; images content unchanged, renamed by hash. Same original creators and CC BY-SA 4.0 attribution/ShareAlike obligations above, with Figshare conflict retained. Whole country groups preserve existing train/val/test. Selection/exclusions/source XML and background import records retained.

## CivicEye Colab cleanup modification
Reviewed 275 active RDD positive images using annotated whole-image/box-crop sheets. Excluded 42 images (66 original class-0 boxes): 17 visually clear crack/seam/slab-repair cases and 25 ambiguous surface/edge-damage cases conservatively withheld for CivicEye target semantics. Original data/annotations remain preserved outside active export. No retained images reassigned across splits. This is subset selection, not a claim of original-author annotation correction. Original CC BY-SA/attribution and Figshare discrepancy above remain in effect.
