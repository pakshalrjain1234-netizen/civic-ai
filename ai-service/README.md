# CivicEye ONNX inference service

Production inference dependencies only: FastAPI, Uvicorn, ONNX Runtime CPU,
OpenCV headless, NumPy, Pillow and python-dotenv. JSON/base64 requests do not
require python-multipart. No PyTorch, training package, OpenAI key or paid API.

The service loads the unchanged models/version-2/civiceye-v2.onnx and filters its
outputs to garbage and waterlogging. Automatic potholes are disabled. V1 and
rejected candidates remain in the original project archives, not this deployment.

Local: python -m uvicorn main:app --host 127.0.0.1 --port 8000
Render: python start.py (0.0.0.0, PORT from the environment, one worker).
Build: pip install -r requirements.txt && python verify_model.py

/health is public. When V2 really loads, model_loaded and
garbage_waterlogging_detector are true and ready is true for these supported
classes. pothole_detector and automatic_pothole_ready remain false. Failures
report model_error and false detector state. No model load is simulated.
POST /detect accepts an image field containing base64 or a data URI; responses
contain real ONNX boxes and confidence. Health/detection responses use no-store.
Body/image limits and a single-flight inference lock prevent overlapping work.

CORS allows only the named Netlify origin plus explicit localhost development
origins; no wildcard and no browser credentials. See ../render.yaml and
../DEPLOYMENT.md for the exact settings and remaining deployment steps.

On Render, inference_location reports render and cloud_inference is true because
frames are processed on your own hosted service. The detector itself remains the
free ONNX model, not an external model API. Local hosting reports local/false.
No images are saved by this API and no detection result is permanently cached.
