# Download and import real CivicEye data

Run commands from the `ai-service` folder, with Python and its requirements installed. All commands below prepare data; none train a model. Class IDs remain 0 pothole, 1 garbage, 2 waterlogging. The target is 200–400 useful photos per class plus 30–60 annotated physical-demo frames.

## 1. Potholes: RDD2022

Official authors' links: https://github.com/sekilab/RoadDamageDetector and https://figshare.com/articles/dataset/21431547 . The original author repository image-license notice specifies **CC BY-SA 4.0**. The official Figshare record instead says CC BY 4.0; this conflict is preserved in licenses/RDD2022-license-verification.json. CivicEye retains attribution and ShareAlike for imported RDD image/annotation derivatives pending author clarification. See licenses/ATTRIBUTION.md.

Download **RDD2022_India.zip** (about 502 MiB) from the country-specific links in the official README. If that link gives 403, the official Figshare combined archive contains `RDD2022/India.zip`; the combined file is about 13 GB, so prefer a country archive or the provided bounded range downloader instead of downloading all countries.

Place the country ZIP at `ai-service/data-sources/pothole/RDD2022_India.zip`. You may instead place its extracted `India/train/images` and `India/train/annotations/xmls` tree here. The importer discovers images and XML recursively, keeps only **D40 pothole** boxes, and skips crack-only images. Official test images without annotations are not used.

```
python scripts/import_real_dataset.py import --kind rdd --source data-sources/pothole/RDD2022_India.zip --limit 200
```

The selected source subsets are at `data-sources/pothole/RDD2022_India/`, `RDD2022_Czech/` and `RDD2022_China_MotorBike/` and can be imported directly. Review the full image for other CivicEye objects which may need additional annotation. Default RDD grouping keeps an entire country together because trustworthy recording IDs are unavailable. The active dataset uses India for train, Czech for validation and China MotorBike for test. Never invent independence by randomly splitting consecutive road frames.

## 2. Litter: TACO v0.1 archive

Official dataset record: https://zenodo.org/records/3587843 (linked by https://github.com/pedropro/TACO). The **dataset record** has CC BY 4.0; the toolkit's MIT license is separate. Use the matching archive and annotations from this record rather than assuming every later Flickr image has the same verified rights. Attribution: Pedro F. Proença and Pedro Simões, TACO: Trash Annotations in Context for Litter Detection (2020).

If automatic bounded retrieval fails, download **TACO.zip** from this record (2.7 GB), place it at `ai-service/data-sources/garbage/TACO.zip`. Do not download unlabelled or unofficial images. The importer reads `TACO/data/annotations.json` and the corresponding `batch_*` folders, converts COCO bounding boxes, maps annotated litter to class 1 and generates unique names.

```
python scripts/import_real_dataset.py import --kind taco --source data-sources/garbage/TACO.zip --limit 200
```

The downloaded 640-size subsets are already imported: `data-sources/garbage/TACO-640` and `data-sources/garbage/TACO-640-diverse`, with 339 unique photos after deduplication. These use URLs from the published-release annotations with scaled boxes. TACO contains individual litter in diverse settings, including beaches/woods; it is useful prototype material but does not replace garbage-pile and local street photos. Visually reject irrelevant scenes and add missed CivicEye objects before final approval. Default groups keep each batch together conservatively; review collector/session identities if available.

## 3. Street-level waterlogging: original Roadway Flooding release

The main source is the original-author **Image Dataset for Roadway Flooding** release: https://data.mendeley.com/datasets/t395bwcvbw/1 , **CC BY 4.0**, DOI 10.17632/t395bwcvbw.1. Creators: Cem Sazara, Mecit Cetin, Khan Iftekharuddin. The archive has already been downloaded directly and 200 reviewed street-level photos imported. Its extracted image/mask pairs and selection.json are at `data-sources/waterlogging/RoadwayFlooding/extracted/Dataset/`.

```
python scripts/import_real_dataset.py import --kind roadway --source data-sources/waterlogging/RoadwayFlooding/extracted/Dataset --limit 200
```

Binary PNG mask foreground **1** becomes class 2; each 8-connected region of at least 500 pixels yields its enclosing rectangle. Background 0 is ignored. Boxes can cover irregular water edges and exclude small fragments; review them against the retained masks before approval. Only the 200 scene-reviewed IDs in selection.json are imported.

**IRDID is not cleared for import:** https://github.com/ahs695/Indian-Road-Damage-Infrastructure-Dataset declares CC BY 4.0, but original water-photo rights are unspecified and its labels are classification-only. There are only 96 unique water image blobs behind 200 filenames. Do not use the supplied random splits, manufacture detection boxes, or duplicate photos. To reconsider it, obtain per-photo original URL, creator, exact license/permission, real bounding boxes and scene/session groups; then review and deduplicate. See licenses/IRDID/audit.json.

FRED was also researched as an author-collected street-level alternative (https://huggingface.co/datasets/CMalone-Jupiter/FRED, CC BY-NC-SA 4.0). Public metadata is accessible but image/card retrieval is gated and returned HTTP 401; it was not imported. No gated-access bypass was attempted.

## 3a. Supplement only: FloodNet supervised v1.0

Official source: https://github.com/BinaLab/FloodNet-Supervised_v1.0 . Follow its **Dropbox** link. License: **CDLA Permissive 1.0**, https://cdla.io/permissive-1-0/ . Keep license and attribution to Rahnemoonfar et al., FloodNet (2021), DOI 10.1109/ACCESS.2021.3090981.

The Dropbox page was accessible, but its initial 16 exposed matching pairs yielded no masks with enough road-flooded pixels; no images were imported. Download image/mask pairs from the supervised dataset, preserving `train/train-org-img` and `train/train-label-img` (and the corresponding validation/test folders, if available). For a small prototype, select up to 200–400 pairs whose masks contain **class 3: road flooded**. Keep each JPG and its matching PNG mask; `12345.jpg` matches `12345_lab.png`. Place the extracted tree at `ai-service/data-sources/waterlogging/FloodNet/`, or its ZIP at `ai-service/data-sources/waterlogging/FloodNet.zip`.

```
python scripts/import_real_dataset.py import --kind floodnet --source data-sources/waterlogging/FloodNet --limit 200
```

FloodNet is aerial-domain data, training-only and capped at 20% of external real waterlogging images by the merge tool. Only indexed mask value **3** becomes CivicEye class 2. Generic water, pools, flooded buildings and unrelated classes are excluded. Connected-component bounding boxes (minimum 500 pixels by default) are derived proposals: inspect them manually, especially roads broken into several mask fragments. FloodNet is aerial imagery; supplement it with legally obtained phone-view flooded-road photos. Without verified flight/scene groups, the importer conservatively keeps FloodNet together; it cannot certify independent evaluation splits from filenames alone.

## 4. Your physical demonstration

Record several separate sessions with different lighting/viewpoints. Use your own recordings with permission. Extract up to 60 frames per video:

```
python scripts/extract_video_frames.py input.mp4 data-sources/physical-demo/session01 --interval 1 --session session01 --max-frames 60
```

Use the **same session name for related clips** from one setup. Review sharpness, diversity and near duplicates, then annotate 30–60 useful frames using YOLO IDs 0/1/2. Save each label TXT beside its JPG. An empty TXT means a deliberately reviewed negative. Missing TXT means unannotated and is skipped. Keep `frame_manifest.csv`; never divide one recording/session across splits.

```
python scripts/import_real_dataset.py import --kind physical --source data-sources/physical-demo/session01 --owned
```

## 5. Merge, inspect, approve

For external sources, an optional CSV with columns `image,group` assigns verified scene/session identities; image paths are relative to the supplied extracted source. Pass it as `--groups groups.csv`. Every imported image must have a row. Group identifiers must also match across sources/clips depicting the same session. `--group session01` can conservatively force a whole import together.

```
python scripts/import_real_dataset.py merge --synthetic-fraction 0.20
python scripts/dataset_tools.py dataset
```

The merge keeps groups intact with a deterministic approximate 70/20/10 allocation of real images. Large groups can prevent exact percentages. Synthetic images go only into training; default 20% of total images means 80% real. It automatically backs up the active dataset to a dated `data-sources/dataset-before-merge-*` folder before rebuilding. It writes provenance, validation statistics and READINESS.json. Converted source images remain in `data-sources/converted`.

**Before training:** obtain all classes in every split, review group independence and near duplicates, inspect all boxes and relevant domain coverage, check source licenses/attribution, and approve the dataset. Syntactically valid labels do not establish accuracy. Missing real waterlogging or independent pothole groups means the dataset is still incomplete.
