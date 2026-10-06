import hashlib
import json
import math
from pathlib import Path
import sys
from datetime import datetime, timezone
from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.classes import CLASS_NAMES, validate_class_names

IMAGE_SUFFIXES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}


def validate_label_line(line, description='label'):
    parts = line.split()
    if len(parts) != 5 or parts[0] not in {'0', '1', '2'}:
        raise ValueError(f'{description}: expected class_id x_center y_center width height; class_id must be 0, 1, or 2.')
    try:
        x, y, width, height = map(float, parts[1:])
    except ValueError as exc:
        raise ValueError(f'{description}: coordinates must be numbers.') from exc
    if not all(math.isfinite(v) for v in (x, y, width, height)) or not (0 <= x <= 1 and 0 <= y <= 1 and 0 < width <= 1 and 0 < height <= 1):
        raise ValueError(f'{description}: coordinates must be normalized to 0–1, with positive width/height.')
    if x-width/2 < -1e-6 or y-height/2 < -1e-6 or x+width/2 > 1+1e-6 or y+height/2 > 1+1e-6:
        raise ValueError(f'{description}: bounding box extends outside the image.')
    return int(parts[0])


def prepare_dataset(data_path, required_splits=('train', 'val'), require_all_classes=True):
    data_path = Path(data_path).expanduser().resolve()
    if not data_path.is_file():
        raise ValueError(f'Dataset YAML not found: {data_path}')
    config = yaml.safe_load(data_path.read_text(encoding='utf-8'))
    if not isinstance(config, dict) or config.get('nc') != 3:
        raise ValueError('dataset.yaml must define nc: 3 and the frozen CivicEye names.')
    validate_class_names(config.get('names'))
    if config.get('download'):
        raise ValueError('Automatic dataset downloads are not permitted. Supply your team-owned dataset locally.')
    base = Path(config.get('path', '../dataset')).expanduser()
    if not base.is_absolute():
        base = data_path.parent / base
    base = base.resolve()
    config['path'] = str(base)
    hashes = {}
    summary = {}
    for split in required_splits:
        value = config.get(split)
        if not isinstance(value, str):
            raise ValueError(f'{split} must point to an images/{split} directory.')
        images_dir = Path(value)
        if not images_dir.is_absolute():
            images_dir = base / images_dir
        images_dir = images_dir.resolve()
        if images_dir.parent.name != 'images':
            raise ValueError(f'Use the dataset/images/{split} layout so image-label pairing is unambiguous.')
        labels_dir = images_dir.parent.parent / 'labels' / images_dir.name
        images = sorted(p for p in images_dir.rglob('*') if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES) if images_dir.exists() else []
        if not images:
            raise ValueError(f'No real images in {images_dir}. Add sourced/labeled images before training or validation.')
        counts = {name: 0 for name in CLASS_NAMES.values()}
        negatives, missing_labels = 0, 0
        expected_labels = set()
        for image_path in images:
            with Image.open(image_path) as image:
                image.verify()
            digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
            previous = hashes.get(digest)
            if previous and previous[0] != split:
                raise ValueError(f'Dataset leakage: identical image in {previous[0]} and {split}: {previous[1]} / {image_path}')
            hashes[digest] = (split, image_path)
            label_path = labels_dir / image_path.relative_to(images_dir).with_suffix('.txt')
            if label_path in expected_labels:
                raise ValueError(f'Multiple images share label {label_path}; use unique image stems.')
            expected_labels.add(label_path)
            lines = [line.strip() for line in label_path.read_text(encoding='utf-8-sig').splitlines() if line.strip()] if label_path.exists() else []
            if not label_path.exists():
                missing_labels += 1
            if not lines:
                negatives += 1
            for number, line in enumerate(lines, 1):
                class_id = validate_label_line(line, f'{label_path}:{number}')
                counts[CLASS_NAMES[class_id]] += 1
        orphaned = [p for p in labels_dir.rglob('*.txt') if p not in expected_labels] if labels_dir.exists() else []
        if orphaned:
            raise ValueError(f'Orphan label with no matching image: {orphaned[0]}')
        if require_all_classes and any(n == 0 for n in counts.values()):
            raise ValueError(f'{split} needs real positive labels for all three classes. Found {counts}.')
        summary[split] = {'images': len(images), 'background_images': negatives, 'missing_label_files': missing_labels, 'objects': counts}
        config[split] = str(images_dir)
    # Resolve every configured split, including an optional as-yet-empty test directory.
    for split in ('train', 'val', 'test'):
        if isinstance(config.get(split), str):
            path = Path(config[split])
            config[split] = str(path if path.is_absolute() else base / path)
    return config, summary


def save_resolved_dataset(config):
    target = ROOT / 'training' / 'prepared'
    target.mkdir(parents=True, exist_ok=True)
    filename = target / ('dataset-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f') + '.yaml')
    filename.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
    return filename


def print_summary(summary):
    print(json.dumps(summary, indent=2))
    for split, values in summary.items():
        if values['missing_label_files']:
            print(f"NOTE: {split} has {values['missing_label_files']} images without labels, treated as backgrounds. Confirm these are genuine negatives.")
