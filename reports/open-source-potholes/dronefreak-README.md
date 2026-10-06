---
license: agpl-3.0

pipeline_tag: object-detection

library_name: ultralytics

datasets:
  - dronefreak/RDD2022

tags:
  - object-detection
  - detectionbench
  - ultralytics
  - pytorch
  - computer-vision
  - road-damage
  - pavement-distress
  - infrastructure
  - pothole-detection
  - autonomous-driving
metrics:
  - map50
  - map50-95
  - precision
  - recall
  - f1

base_model: "Ultralytics/YOLOv8"

model-index:
  - name: YOLOv8m Finetuned on RDD2022 Road Damage
    results:
      - task:
          type: object-detection
          name: Object Detection
        dataset:
          name: RDD2022 Road Damage
          type: rdd2022
        metrics:
          - type: mAP50
            value: 62.03
            name: mAP@50 (test split)
          - type: mAP50-95
            value: 34.08
            name: mAP@50-95 (test split)
          - type: precision
            value: 65.61
            name: Precision (test split)
          - type: recall
            value: 57.42
            name: Recall (test split)
        source:
          url: https://github.com/dronefreak/DetectionBench
          name: DetectionBench
---


# YOLOv8m Finetuned on RDD2022 Road Damage

Fine-tuned YOLOv8m object detector on the **RDD2022 Road Damage** benchmark dataset, trained and evaluated as part of [DetectionBench](https://github.com/dronefreak/DetectionBench) -- a framework for reproducibly benchmarking modern object detectors with identical training recipes and evaluation metrics across multiple real-world datasets.

<p align="center">
  <img src="rdd2022_yolov8m_showcase.jpg" alt="RDD2022 Road Damage Detection Demo" width="900">
</p>

<br>

<!-- ROW 1: Identity & Tech Stack -->
<div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
  <img src="https://img.shields.io/badge/Task-Object_Detection-blue?style=flat-square" alt="Task">
  <img src="https://img.shields.io/badge/Framework-Ultralytics_YOLO-0aa1a7?style=flat-square" alt="Framework">
  <img src="https://img.shields.io/badge/Base_Model-YOLOv8m-purple?style=flat-square" alt="Base Model">
</div>

<!-- ROW 2: Performance Metrics -->
<div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
  <img src="https://img.shields.io/badge/mAP@50-62.03%25-success?style=flat-square" alt="mAP@50">
  <img src="https://img.shields.io/badge/mAP@50:95-34.08%25-orange?style=flat-square" alt="mAP@50:95">
  <img src="https://img.shields.io/badge/Params-25.9M-lightgrey?style=flat-square" alt="Params">
</div>

<!-- ROW 3: Metadata -->
<div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 24px; flex-wrap: wrap;">
  <img src="https://img.shields.io/badge/License-AGPL--3.0-lightgrey?style=flat-square" alt="License">
  <a href="https://github.com/dronefreak/DetectionBench"><img src="https://img.shields.io/badge/Source-DetectionBench-black?style=flat-square" alt="Source"></a>
</div>

---

## Usage

### Install Dependencies

```bash
pip install ultralytics huggingface_hub
```

### Load Model from Hugging Face

```python
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

weights = hf_hub_download(
    repo_id="dronefreak/rdd2022-yolov8m",
    filename="best.pt"
)

model = YOLO(weights)
```

### Run Inference

```python
results = model.predict(
    source="image.jpg",
    conf=0.25
)

results[0].show()
```
---

## Performance

Evaluated on the RDD2022 Road Damage **test** split, using DetectionBench's standard evaluation pipeline (`detectionbench-evaluate`).

| Metric     | Score (%)       |
| ---------- | --------------- |
| mAP@50     | 62.03     |
| mAP@50-95  | 34.08   |
| Precision  | 65.61 |
| Recall     | 57.42    |
| F1 Score   | 61.24        |
| Parameters | 25.9M    |
| FLOPs      | 78.9B (at 640 px)     |

---

## RDD2022 Road Damage Model Zoo

Every model DetectionBench has trained and evaluated on RDD2022 Road Damage so far, for full transparency -- see [DetectionBench](https://github.com/dronefreak/DetectionBench) for the smaller, curated comparison set used on the project README.

| Model                | mAP@50        | mAP@50-95       | Precision         | Recall         |
| --------------------- | ------------- | --------------- | ----------------- | -------------- |
| RF-DETR Medium | 65.08 | 36.02 | 71.18 | 55.98 |
| RF-DETR Small | 64.71 | 35.73 | 65.69 | 59.41 |
| **YOLOv8m** | **62.03** | **34.08** | **65.61** | **57.42** |
| YOLOv8s | 61.45 | 33.53 | 64.55 | 57.18 |
| YOLO26s | 61.27 | 33.3 | 64.42 | 57.13 |
| YOLO26m | 61.24 | 33.38 | 63.7 | 57.27 |
| RF-DETR Nano | 60.85 | 33.22 | 65.49 | 54.3 |
| YOLOv8n | 58.8 | 32.05 | 62.03 | 56.08 |
| YOLO11x | 51.05 | 26.54 | 56.64 | 49.54 |
---

## Per-Class Performance

| Class                      | mAP@50          | mAP@50-95         |
| -------------------------- | --------------- | ----------------- |
| longitudinal_crack       | 55.97 | 30.69 |
| transverse_crack       | 55.52 | 26.6 |
| alligator_crack       | 62.5 | 32.91 |
| pothole       | 74.15 | 46.12 |

![Normalized Confusion Matrix](confusion_matrix_normalized.png)

---

## Dataset

This model was trained on **RDD2022 Road Damage**. For the full dataset description, provenance, license, and citation, see the dataset card:

https://huggingface.co/datasets/dronefreak/RDD2022

### Classes

* longitudinal_crack
* transverse_crack
* alligator_crack
* pothole
---

## Training Configuration

| Setting          | Value                           |
| ---------------- | -------------------------------- |
| Dataset          | RDD2022 Road Damage       |
| Framework        | Ultralytics YOLO                  |
| Training Toolkit | DetectionBench                   |
| Epochs (configured max) | 50 |
| Epochs (actually trained) | 50 |
| Early Stopping Patience | 10 |
| Batch Size | 16 |
| Image Size | 640 |
| Optimizer | Adam |
| Initial Learning Rate | 0.001 |
| Seed | 0 |
---

## Repository Contents

```text
best.pt
results.csv
args.yaml
BoxPR_curve.png
BoxF1_curve.png
BoxP_curve.png
BoxR_curve.png
confusion_matrix.png
confusion_matrix_normalized.png
val_batch0_pred.jpg
rdd2022_yolov8m_showcase.jpg
README.md
```

---

## Related Resources

* [RDD2022 Road Damage dataset card](https://huggingface.co/datasets/dronefreak/RDD2022) on Hugging Face
* [DetectionBench](https://github.com/dronefreak/DetectionBench) -- reproducible benchmarks for modern object detectors on real-world datasets
* [RDD2022 paper preprint (arXiv:2209.08538)](https://arxiv.org/abs/2209.08538)
* [RDD2022 project repository (official data source)](https://github.com/sekilab/RoadDamageDetector)

---

## Training Framework

This model was trained using [DetectionBench](https://github.com/dronefreak/DetectionBench), an open-source framework for benchmarking object detectors across multiple real-world datasets with a common pipeline.

Features include:

* A dataset-adapter registry for converting real-world datasets into a canonical format
* Identical training/evaluation recipes across model families (Ultralytics YOLO/RT-DETR, RF-DETR)
* Hardware profiling (latency, FPS, VRAM, parameters, FLOPs)
* One-command reproducibility via versioned Hydra configs

If you find this model useful, please consider starring the repository.

---

## Known Limitations

* Not comparable to the official CRDDC2022 leaderboard: the challenge test set has no public labels, so the `test` split here is a held-out 15% slice (70/15/15 split) of the publicly-labelled images, merged across countries -- scores are only comparable between the models listed in this card's Model Zoo.
* Class imbalance: `longitudinal_crack` (44.0%) is the most common class, while `pothole` (18.1%) and `alligator_crack` (17.9%) are the rarest of the four -- per-class accuracy differs noticeably between them.
* Four-class taxonomy only: the source data's 5th "other" bucket (block cracks, road repairs and country-specific codes, ~6.5k boxes) was dropped to match the four damage types the CRDDC2022 challenge scores, so those damage types are not detected.
* Sparse, thin targets: about a third of images contain no in-taxonomy damage (clean-road frames), with 1.5 boxes per image on average, and cracks are thin structures that are easily lost when large frames (some over 4000 pixels wide) are downscaled to the model's input size.
* Uneven country and imaging-setup mix: the images come from six countries and several capture setups (smartphone, dashboard camera, drone) in very different proportions, so performance can vary substantially by country and generalization to unseen regions or damage conventions is untested.
* Share-alike data: the RDD2022 images are CC BY-SA 4.0 -- see the Dataset section above for attribution and the dataset card for the full terms.
---

## Citation

If you use this model in your research, please consider citing the dataset and the model architecture:

```
@article{arya2022rdd2022,
  title = {RDD2022: A multi-national image dataset for automatic Road Damage Detection},
  author = {Arya, Deeksha and Maeda, Hiroya and Ghosh, Sanjay Kumar and Toshniwal, Durga and Sekimoto, Yoshihide},
  journal = {arXiv preprint arXiv:2209.08538},
  year = {2022}
}
```

```bibtex
No official YOLOv8 research paper has been published by Ultralytics; this is their own recommended software citation instead:

@software{jocher2023yolov8,
  author = {Glenn Jocher and Ayush Chaurasia and Jing Qiu},
  title = {Ultralytics YOLOv8},
  version = {8.0.0},
  year = {2023},
  url = {https://github.com/ultralytics/ultralytics},
  license = {AGPL-3.0}
}
```