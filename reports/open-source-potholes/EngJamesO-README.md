---
license: mit
pipeline_tag: object-detection
tags:
- computer-vision
- object-detection
- pothole-detection
- yolov8
- yolov9
- yolov11
- yolov12
library_name: ultralytics
language:
- en
---

# Pothole Detection Models

This repository contains trained YOLO models for detecting potholes in road images. The models were developed to assist with road infrastructure monitoring and maintenance planning.

## Model Overview

Five YOLO architectures were trained and evaluated for pothole detection:

| Model | Parameters | mAP50 | mAP50-95 | Latency (ms) | FPS |
|-------|-----------|-------|----------|--------------|-----|
| YOLOv9c | 25.3M | 0.792 | 0.485 | 36.3 | 27.6 |
| YOLOv12n | 2.56M | 0.785 | 0.463 | 13.9 | 72.1 |
| YOLOv8n | 3.01M | 0.782 | 0.465 | 6.9 | 144.7 |
| YOLOv11 | 2.58M | 0.779 | 0.460 | 9.3 | 107.0 |
| YOLOv8-FPN | 2.21M | 0.707 | 0.396 | 6.4 | 155.8 |

## Intended Uses

- **Primary Use**: Automated pothole detection in road images for infrastructure assessment
- **Secondary Use**: Research in object detection, computer vision applications for transportation
- **Target Users**: Road maintenance departments, urban planners, researchers

## Model Selection Guide

- **YOLOv9c**: Best overall accuracy (mAP50: 0.792), recommended when accuracy is prioritized over speed
- **YOLOv8n**: Good balance of accuracy and speed, suitable for real-time applications
- **YOLOv12n**: Lightweight with competitive accuracy, ideal for edge deployment
- **YOLOv11**: Efficient architecture with modern optimizations
- **YOLOv8-FPN**: Fastest inference, suitable for high-throughput scenarios

## Performance at Different Confidence Thresholds

Based on qualitative evaluation (40 test images, 86 ground truth objects):

### YOLOv9c (Recommended)
- **Conf=0.25**: Precision: 0.804, Recall: 0.831, F1: 0.790
- **Conf=0.50**: Precision: 0.846, Recall: 0.723, F1: 0.753
- **Conf=0.70**: Precision: 0.700, Recall: 0.505, F1: 0.558

### YOLOv8n
- **Conf=0.25**: Precision: 0.807, Recall: 0.838, F1: 0.791
- **Conf=0.50**: Precision: 0.840, Recall: 0.710, F1: 0.751
- **Conf=0.70**: Precision: 0.600, Recall: 0.437, F1: 0.482

## Usage

### Installation

```bash
pip install ultralytics opencv-python
```

### Python inference

```python
from ultralytics import YOLO

# Load model
model = YOLO("yolov9c.pt")

# Run inference
results = model("path/to/image.jpg")

# Visualize results
results[0].show()
```

### Limitations

- Models trained on specific road conditions; performance may vary on different terrain or weather conditions
- Detection accuracy depends on image quality and resolution
- Models may have difficulty with very small or heavily obscured potholes
- Performance not validated on night-time or extreme weather images
