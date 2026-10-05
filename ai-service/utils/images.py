import base64
import binascii
import io
import warnings
from PIL import Image, ImageOps, UnidentifiedImageError


def decode_frame(data_url: str, max_bytes: int):
    """Decode client JPEG/PNG/WebP data URLs. Reject oversized or corrupt images."""
    if not isinstance(data_url, str) or ',' not in data_url:
        raise ValueError('A base64 image data URL is required.')
    header, encoded = data_url.split(',', 1)
    if header not in {'data:image/jpeg;base64', 'data:image/png;base64', 'data:image/webp;base64'}:
        raise ValueError('Use a JPEG, PNG, or WebP image.')
    if len(encoded) > ((max_bytes + 2) // 3) * 4:
        raise ValueError('Image exceeds the allowed upload size.')
    try:
        content = base64.b64decode(encoded, validate=True)
        if len(content) > max_bytes:
            raise ValueError('Image exceeds the allowed upload size.')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                if image.width * image.height > 16_000_000:
                    raise ValueError('Image has too many pixels. Send a compressed camera frame.')
                image.load()
                return ImageOps.exif_transpose(image).convert('RGB')
    except (binascii.Error, UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError('The image is corrupt or cannot be decoded.') from exc
