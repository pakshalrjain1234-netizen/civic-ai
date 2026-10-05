"""Frozen CivicEye v1 class IDs shared by training and inference."""
CLASS_NAMES = {0: 'pothole', 1: 'garbage', 2: 'waterlogging'}


def validate_class_names(names):
    try:
        actual = {int(k): str(v) for k, v in names.items()} if isinstance(names, dict) else dict(enumerate(names))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError('Invalid model class mapping. Expected 0=pothole, 1=garbage, 2=waterlogging.') from exc
    if actual != CLASS_NAMES:
        raise ValueError(f'Incorrect CivicEye weights: expected exactly {CLASS_NAMES}, found {actual}. Model remains unloaded.')
    return actual
