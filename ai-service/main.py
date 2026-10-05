import asyncio
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from time import perf_counter
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from utils.hybrid import HybridDetector
from utils.images import decode_frame

ROOT = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except ImportError:
    pass
logger = logging.getLogger('civiceye.vision')
MAX_BYTES = int(os.getenv('CIVICEYE_MAX_IMAGE_BYTES', '5242880'))
MAX_BODY = ((MAX_BYTES + 2) // 3) * 4 + 100_000
detector = HybridDetector(ROOT, float(os.getenv('CIVICEYE_CONFIDENCE', '.35')))


@asynccontextmanager
async def lifespan(app):
    await run_in_threadpool(detector.load)
    app.state.inference_lock = asyncio.Lock()
    yield
    detector.close()


app = FastAPI(title='CivicEye hybrid vision', version='3.0.0', lifespan=lifespan)
origins = [s.strip().rstrip('/') for s in os.getenv('CIVICEYE_CORS_ORIGINS', 'https://dashing-speculoos-a9724c.netlify.app,http://127.0.0.1:5189,http://localhost:5189').split(',') if s.strip()]
if '*' in origins:
    raise ValueError('CivicEye requires explicit CORS origins; wildcard is not allowed.')
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type'])


@app.middleware('http')
async def no_inference_cache(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in ('/health', '/detect'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.middleware('http')
async def body_limit(request: Request, call_next):
    if request.method == 'POST':
        length = request.headers.get('content-length')
        try:
            if length and int(length) > MAX_BODY:
                return JSONResponse({'success': False, 'error': 'Image upload too large.'}, 413)
        except ValueError:
            return JSONResponse({'success': False, 'error': 'Invalid content length.'}, 400)
        # Bound chunked requests too, before JSON decoding.
        data = bytearray()
        async for chunk in request.stream():
            data.extend(chunk)
            if len(data) > MAX_BODY:
                return JSONResponse({'success': False, 'error': 'Image upload too large.'}, 413)
        request._body = bytes(data)
    return await call_next(request)


class FrameRequest(BaseModel):
    model_config = ConfigDict(extra='ignore')
    image: str = Field(min_length=10, max_length=MAX_BODY)


@app.get('/health')
async def health():
    return detector.health()


@app.post('/detect')
async def detect(payload: FrameRequest):
    if detector.model is None:
        return JSONResponse({'success': False, 'error': 'MODEL_NOT_LOADED', 'message': detector.error,
                             'detections': []}, 503)
    lock = app.state.inference_lock
    if lock.locked():
        return JSONResponse({'success': False, 'error': 'INFERENCE_BUSY',
                             'message': 'Previous inference is still running. Retry shortly.'}, 429)
    started = perf_counter()
    async with lock:
        try:
            image = await run_in_threadpool(decode_frame, payload.image, MAX_BYTES)
        except ValueError as exc:
            return JSONResponse({'success': False, 'error': str(exc)}, 400)
        try:
            detections = await run_in_threadpool(detector.detect, image)
        except Exception:
            logger.exception('ONNX inference failed')
            return JSONResponse({'success': False, 'error': 'AI detection temporarily unavailable.'}, 503)
    return {'success': True, 'processingTimeMs': round((perf_counter() - started) * 1000, 1),
            'detections': detections, 'ready': detector.health()['ready'],
            'pothole_pending': False,
            'warnings': [detector.warning] if detector.warning else []}
