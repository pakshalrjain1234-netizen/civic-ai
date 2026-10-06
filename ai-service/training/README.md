> LOCAL INFERENCE UPDATE: use the delivered Colab notebook for training and export. The API now loads models/civiceye.onnx with ONNX Runtime and local requirements.txt. PyTorch/Ultralytics belong only in training/requirements.txt. Keep best.pt/civiceye.pt as original checkpoints; a .pt copy no longer loads in the local API. See ../../CivicEye_Colab_Guide.md for current deployment instructions. Historical command reference follows.

# Train the first real CivicEye model

This prepares a real transfer-learning workflow. A synthetic starter set has been integrated and licensed real subsets have been prepared. See [the dataset report](../DATASET_REPORT.md), [sources](../DATASET_SOURCES.md) and [download/import guide](../REAL_DATA_DOWNLOAD_GUIDE.md) for current counts and missing data. **No model has been trained. Do not start final training until the dataset is reviewed and the user approves it.**

The frozen class IDs are **0 pothole, 1 garbage, 2 waterlogging**. Do not add classes or reorder them. Both training scripts and the API check this exact mapping. We start from the compact [Ultralytics YOLO11 nano detection model](https://docs.ultralytics.com/models/yolo11); pretrained weights are downloaded by Ultralytics only when you explicitly run training with a prepared dataset.

## 1. Add your team's sourced images

Place your project here, or use the existing checkout. All commands below run from ai-service:

```powershell
cd 'C:\Users\hp\Documents\Codex\2026-10-02\files-pasted-by-the-user-build\outputs\civiceye-ai\ai-service'
```

Directory layout:

```text
ai-service/
├── dataset/
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── labels/
│       ├── train/
│       ├── val/
│       └── test/
├── models/
├── training/
│   ├── common.py
│   ├── dataset.yaml
│   ├── train.py
│   ├── validate.py
│   └── README.md
├── main.py
└── requirements.txt
```

The .gitkeep files only preserve empty folders; they are not training data.

Use permitted real-road photos and photos of your physical tray/road demonstration. Include different angles, lighting, distances, dry/wet surfaces, and backgrounds. Label only visible civic issues. A water-filled depression may be labeled waterlogging; do not label invisible drain blockage.

Split by collection session, road/location, or physical-demo setup, not by adjacent video frames. Keep related frames and near-duplicates together in one split. A starting allocation is about 70% train, 20% val, 10% test, adjusted for your dataset size. Include real-road and demonstration examples in the held-out sets. The preflight detects identical-file leakage but cannot identify every near-duplicate.

Train is used to learn. Val guides model selection. Keep test untouched until you want a final independent evaluation. Each train/val split must contain genuinely labeled examples of all three classes. Test is optional until you run test evaluation.

## 2. Create matching labels

An image `dataset/images/train/road_001.jpg` pairs with `dataset/labels/train/road_001.txt`. Use unique stems. Nested directories are supported as long as the image/label structure matches.

Use an annotation tool that exports YOLO **detection bounding boxes**. Each object occupies one line:

```text
class_id x_center y_center width height
```

All four coordinates are fractions of the image dimensions, between 0 and 1. For example, an actual pothole box centered at 50% across and 60% down, occupying 20% width and 15% height, would be:

```text
0 0.50 0.60 0.20 0.15
```

This is a format explanation, not a supplied dataset annotation. Measure each box against its own real image. Do not paste illustrative coordinates into arbitrary images. Multiple visible objects need multiple lines. No header, confidence, pixel coordinates, polygons, or random labels belong in these detection label files.

For negative/background images (normal road, clean surface, dry sand, normal objects), use an **empty** matching .txt file. Missing label files are also accepted by YOLO as negatives; the preflight counts and warns about them so accidentally unannotated positives can be caught. Inspect each negative to ensure it truly contains no target object. Negative images are not a fourth class. See [Ultralytics dataset format](https://docs.ultralytics.com/datasets/detect).

## 3. Install dependencies

Use your existing ai-service virtual environment. If it has not been created:

```powershell
$python='C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python -m venv .venv
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

These commands use the verified Python path on this computer. On another computer, use an installed Python 3.11/3.12 executable. Ultralytics/PyTorch can be a large installation. Use an appropriate PyTorch GPU build if training on a GPU.

## 4. Check before training

```powershell
.\.venv\Scripts\python.exe training/train.py --check-only
```

This checks real image readability, matched label stems, orphan labels, coordinates, class IDs/counts, background counts, and identical images across train/val. It neither loads pretrained weights nor trains. Empty folders intentionally fail with a clear “dataset not ready” message.

The dataset YAML uses paths relative to its own location. The scripts resolve these into an absolute snapshot before passing data to Ultralytics, so commands work independently of the working directory and also on Colab. Do not rely on direct `yolo data=training/dataset.yaml` path resolution; use the provided scripts.

## 5. Train explicitly

Laptop CPU:

```powershell
.\.venv\Scripts\python.exe training/train.py --epochs 50 --imgsz 640 --batch 8 --device cpu
```

Defaults are YOLO11n, 50 epochs, 640 pixels, batch 8, CPU, workers 0, seed 42. CPU training may be slow; reduce batch/image size if memory is limited, or use a GPU. Configuration flags include --pretrained, --data, --epochs, --imgsz, --batch, --device, --workers, --project, and --name. Use image sizes divisible by 32. `--pretrained yolo11s.pt` selects the larger small model; start with nano for the hackathon.

Google Colab: upload/extract the project and your sourced dataset, enable a GPU runtime, enter ai-service, then run:

```sh
python -m pip install -r requirements.txt
python training/train.py --check-only
python training/train.py --epochs 50 --imgsz 640 --batch 16 --device 0
```

Copy outputs off the ephemeral Colab disk before the runtime ends.

## 6. Locate best.pt and preserve it

The first default run saves:

```text
ai-service/training/runs/civiceye/weights/best.pt
```

It also saves last.pt, results.csv, plots, and other Ultralytics artifacts. Subsequent default runs use civiceye2, civiceye3, etc. to preserve earlier results. Custom --project/--name flags change the location. The script always prints **BEST MODEL** with the actual absolute path.

After successful training and a strict class check, the script copies best.pt to `ai-service/models/civiceye.pt`. It does not move or delete best.pt. If civiceye.pt exists, a timestamped `civiceye.previous-*.pt` backup is saved first. Use `--no-deploy` to train without replacing the serving model.

If copying manually after the first default run:

```powershell
Copy-Item 'training\runs\civiceye\weights\best.pt' 'models\civiceye.pt'
```

Use the actual printed run folder for later runs. Preserve any model you want to keep before manually overwriting it.

## 7. Validate what the model learned

```powershell
.\.venv\Scripts\python.exe training/validate.py --weights training/runs/civiceye/weights/best.pt --split val --device cpu
```

Once the team has a separate labeled test split:

```powershell
.\.venv\Scripts\python.exe training/validate.py --weights models/civiceye.pt --split test --device cpu
```

Validation prints precision, recall, overall mAP50, mAP50–95, per-class mAP50–95, per-class ground-truth counts, and inference speed. Missing classes are reported with null metrics rather than a misleading score. Machine-readable results are saved as civiceye-metrics.json in the printed validation output directory; inspect confusion-matrix plots and sample predictions too. These are [Ultralytics validation metrics](https://docs.ultralytics.com/modes/val).

Precision asks how many detections are correct; low precision suggests false alerts. Recall asks how many real issues are found; low recall suggests missed issues. mAP measures detection performance across confidence thresholds and box-overlap criteria, not just whether training completed. Training success alone is not proof of accuracy. Inspect real roads and the physical demo separately, including clean/background scenes. No accuracy threshold is claimed or guaranteed by this pipeline.

## 8. Restart the API and confirm loading

Stop the running FastAPI process with Ctrl+C in its terminal, then:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
(Invoke-RestMethod 'http://127.0.0.1:8000/health').model_loaded
```

Expected result is True only when trusted weights are loadable with exactly `{0:pothole, 1:garbage, 2:waterlogging}`. Incorrect ordering, extra classes, missing classes, or incompatible weights produce a clear log warning, model_loaded=false, and a useful model_error. Confirm CIVICEYE_MODEL_PATH in ai-service/.env points to models/civiceye.pt if you previously changed it.

The existing frontend health check will show **AI service connected · AI model loaded** after startup. Point the camera at real objects and evaluate the findings. No frontend changes are needed. This pipeline trains bounding-box detection; it does not produce segmentation-based water surfaceCoverage unless you separately provide a compatible segmentation model later.
