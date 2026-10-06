---
license: mit
tags:
  - yolov8
  - object-detection
  - pothole-detection
  - computer-vision
  - pytorch
  - ultralytics
library_name: ultralytics
pipeline_tag: object-detection
---

# Pothole-Finetuned-YOLOv8

A fine-tuned YOLOv8 model for pothole detection in road images. This model is optimized for detecting potholes with high precision and is production-ready.

## Model Details

- **Architecture**: YOLOv8 Medium
- **Task**: Object Detection
- **Framework**: PyTorch
- **Input Size**: 640x640
- **Number of Classes**: 1 (Pothole)
- **Confidence Threshold**: 0.28
- **IOU Threshold**: 0.5

## Training Configuration

- **Epochs**: 40
- **Batch Size**: 64
- **Optimizer**: Auto (SGD/Adam)
- **Patience**: 200
- **Augmentation**: Enabled
- **Mixed Precision (AMP)**: Enabled
- **Training Device**: GPU/CPU

## Performance

This model was trained on a comprehensive pothole detection dataset with data augmentation and regularization techniques applied.

## Usage

### Installation

```bash
pip install ultralytics opencv-python pillow
```

### Quick Start

```python
from ultralytics import YOLO
from PIL import Image

# Load model from Hugging Face
model = YOLO('hf://your-username/Pothole-Finetuned-YOLOv8')

# Inference on image
results = model.predict(source='image.jpg', conf=0.28)

# Print results
for r in results:
    print(r.boxes)
```

### Advanced Usage

```python
from ultralytics import YOLO
import cv2

# Load model
model = YOLO('hf://your-username/Pothole-Finetuned-YOLOv8')

# Inference on video
results = model.predict(source='video.mp4', conf=0.28, save=True)

# Custom confidence threshold
results = model.predict(source='image.jpg', conf=0.35)

# Get results in different formats
for result in results:
    boxes = result.boxes.xyxy  # Box coordinates
    confidences = result.boxes.conf  # Confidence scores
    class_ids = result.boxes.cls  # Class IDs
```

### Batch Inference

```python
from ultralytics import YOLO

model = YOLO('hf://your-username/Pothole-Finetuned-YOLOv8')

# Batch inference
results = model.predict(source='image_folder/', batch=32, conf=0.28)

# Process results
for result in results:
    for box in result.boxes:
        print(f"Detection: {box.xyxy}, Confidence: {box.conf}")
```

## Annotation/Training on Custom Data

You can fine-tune this model on your own pothole dataset:

```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('hf://your-username/Pothole-Finetuned-YOLOv8')

# Train on custom dataset
results = model.train(
    data='path/to/dataset/data.yaml',
    epochs=50,
    imgsz=640,
    batch=32,
    device=0,  # GPU device number
    patience=50
)
```

### Dataset Format

Your dataset should follow YOLO format:
```
dataset/
├── images/
│   ├── train/
│   │   └── *.jpg
│   ├── val/
│   │   └── *.jpg
│   └── test/
│       └── *.jpg
├── labels/
│   ├── train/
│   │   └── *.txt
│   ├── val/
│   │   └── *.txt
│   └── test/
│       └── *.txt
└── data.yaml
```

### data.yaml Example

```yaml
path: /path/to/dataset
train: images/train
val: images/val
test: images/test

nc: 1  # number of classes
names: ['pothole']  # class names
```

## Model Information

- **Base Model**: YOLOv8m
- **Training Dataset**: Comprehensive pothole detection dataset
- **Output**: Bounding box coordinates with confidence scores

## Hardware Requirements

- **Minimum RAM**: 4GB
- **Minimum VRAM**: 2GB (GPU optional)
- **Recommended**: GPU with 6GB+ VRAM for faster inference

## License

This model and its weights are provided as-is for research and commercial use.

## Support & Feedback

For issues, questions, or feedback about this model, please create an issue in the repository.

## Citation

If you use this model in your research, please cite:

```bibtex
@software{pothole_yolov8_2024,
  title={Pothole Detection YOLOv8 Fine-tuned Model},
  author={Your Name},
  year={2024},
  publisher={Hugging Face},
  howpublished={\url{https://huggingface.co/your-username/Pothole-Finetuned-YOLOv8}}
}
```

---

**Last Updated**: January 2026
