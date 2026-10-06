"""YOLO11 raw ONNX inference. Never imports torch or Ultralytics."""
import ast
import json
import logging
import os
from time import perf_counter
from pathlib import Path
from .severity import visual_severity
from .classes import CLASS_NAMES, validate_class_names

logger = logging.getLogger('civiceye.vision')
ONNX_FORMAT = 'yolo11-raw-v1'

def letterbox_tensor(image, image_size=640):
    """PIL RGB -> BGR letterbox -> RGB float32 NCHW, with exact padding."""
    import cv2
    import numpy as np
    width, height = image.size
    gain = min(image_size / width, image_size / height)
    resized_width, resized_height = max(1,round(width*gain)),max(1,round(height*gain))
    bgr = cv2.cvtColor(np.asarray(image.convert('RGB')), cv2.COLOR_RGB2BGR)
    resized = cv2.resize(bgr, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    dw, dh = image_size-resized_width, image_size-resized_height
    left, top = round(dw/2-.1), round(dh/2-.1)
    padded = cv2.copyMakeBorder(resized, top, dh-top, left, dw-left, cv2.BORDER_CONSTANT, value=(114,114,114))
    rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
    tensor = np.ascontiguousarray(rgb.transpose(2,0,1)[None], dtype=np.float32) / np.float32(255)
    return tensor, (gain, left, top, width, height)

def raw_predictions(output):
    """YOLO11 detection head has xywh + 3 class scores, no objectness."""
    import numpy as np
    output = np.asarray(output)
    if output.ndim != 3 or output.shape[0] != 1:
        raise ValueError('Expected batch-one raw YOLO11 detection output.')
    if output.shape[1] == 7 and output.shape[2] > 7: predictions = output[0].T
    elif output.shape[2] == 7 and output.shape[1] > 7: predictions = output[0]
    else: raise ValueError('Expected 7 channels: xywh plus 3 class probabilities. Re-export without embedded NMS.')
    if not np.isfinite(predictions).all(): raise ValueError('ONNX output contains non-finite values.')
    if np.any(predictions[:,4:] < -1e-5) or np.any(predictions[:,4:] > 1+1e-5):
        raise ValueError('Expected probability scores, not logits/objectness.')
    return predictions

def postprocess(output, transform, confidence=.35, iou_threshold=.45, max_detections=100):
    import numpy as np
    predictions = raw_predictions(output)
    classes = predictions[:,4:].argmax(axis=1)
    scores = predictions[np.arange(len(predictions)),4+classes]
    selected = np.flatnonzero((scores >= confidence) & (predictions[:,2] > 0) & (predictions[:,3] > 0))
    if not len(selected): return []
    selected = selected[np.argsort(-scores[selected],kind='stable')[:3000]]
    xywh = predictions[selected,:4]
    boxes = np.concatenate((xywh[:,:2]-xywh[:,2:]/2, xywh[:,:2]+xywh[:,2:]/2),axis=1)
    gain,left,top,width,height = transform
    areas = (boxes[:,2]-boxes[:,0])*(boxes[:,3]-boxes[:,1])
    retained,pending = [],np.arange(len(selected))
    while len(pending) and len(retained) < max_detections:
        current = int(pending[0]);retained.append(current);others=pending[1:]
        if not len(others): break
        intersection_wh = np.maximum(0,np.minimum(boxes[current,2:],boxes[others,2:])-np.maximum(boxes[current,:2],boxes[others,:2]))
        intersection = intersection_wh[:,0]*intersection_wh[:,1]
        ious = intersection / np.maximum(areas[current]+areas[others]-intersection,1e-9)
        suppress = (classes[selected[others]] == classes[selected[current]]) & (ious > iou_threshold)
        pending = others[~suppress]
    detections = []
    for i in retained:
        # NMS in model coordinates, then undo padding/scale and clip.
        mapped = boxes[i].copy()
        mapped[[0,2]] = np.clip((mapped[[0,2]]-left)/gain,0,width)
        mapped[[1,3]] = np.clip((mapped[[1,3]]-top)/gain,0,height)
        x1,y1,x2,y2 = mapped / np.array([width,height,width,height])
        bw,bh = float(x2-x1),float(y2-y1)
        if bw <= 0 or bh <= 0: continue
        detections.append({'class':CLASS_NAMES[int(classes[selected[i]])], 'confidence':round(float(scores[selected[i]]),4),
            'bbox':{'x':float(x1),'y':float(y1),'width':bw,'height':bh}, 'severity':visual_severity(bw*bh)})
    return detections

class CivicDetector:
    def __init__(self, model_path: Path, confidence=.35, image_size=640, device='cpu'):
        self.model_path = Path(model_path)
        self.confidence,self.image_size,self.device = confidence,image_size,device
        self.model,self.error,self.input_name,self.output_name = None,None,None,None

    def load(self):
        self.model,self.error = None,None
        if not self.model_path.is_file():
            self.error = 'ONNX model missing. Place trained civiceye.onnx in models and restart the service.'
            return
        try:
            import onnxruntime as ort
            import numpy as np
            if self.model_path.suffix.lower() != '.onnx': raise ValueError('Local inference requires civiceye.onnx, not a PyTorch checkpoint.')
            if self.image_size != 640 or self.device != 'cpu' or not 0 < self.confidence <= 1:
                raise ValueError('Use CPU ONNX inference, image size 640 and confidence in (0,1].')
            options = ort.SessionOptions()
            options.intra_op_num_threads = max(1,min(4,int(os.getenv('CIVICEYE_ONNX_THREADS','2'))))
            options.inter_op_num_threads = 1
            options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session = ort.InferenceSession(str(self.model_path), sess_options=options, providers=['CPUExecutionProvider'])
            metadata = session.get_modelmeta().custom_metadata_map
            try: names = json.loads(metadata['names'])
            except json.JSONDecodeError: names = ast.literal_eval(metadata['names'])
            validate_class_names(names)
            if metadata.get('task') != 'detect' or metadata.get('civiceye_format') != ONNX_FORMAT:
                raise ValueError('Use the CivicEye notebook ONNX export: YOLO11 raw detection, no embedded NMS.')
            inputs,outputs = session.get_inputs(),session.get_outputs()
            if len(inputs)!=1 or inputs[0].type!='tensor(float)' or inputs[0].shape!=[1,3,640,640]:
                raise ValueError('Expected static float32 input [1,3,640,640].')
            if len(outputs)!=1 or outputs[0].type!='tensor(float)': raise ValueError('Expected one float32 raw detection output.')
            # Actual session warm-up must pass before /health reports loaded.
            raw_predictions(session.run([outputs[0].name],{inputs[0].name:np.zeros((1,3,640,640),dtype=np.float32)})[0])
            self.input_name,self.output_name = inputs[0].name,outputs[0].name
            self.model = session
        except Exception as exc:
            self.error = str(exc) if isinstance(exc,ValueError) else 'ONNX model could not load. Check ONNX Runtime installation, model metadata and service logs.'
            logger.exception('CivicEye ONNX model remains unloaded')

    def detect(self,image):
        return self.detect_profiled(image)[0]

    def detect_profiled(self,image):
        if self.model is None: raise RuntimeError('Model not loaded.')
        started = perf_counter()
        tensor,transform = letterbox_tensor(image,self.image_size)
        preprocessed = perf_counter()
        output = self.model.run([self.output_name],{self.input_name:tensor})[0]
        inferred = perf_counter()
        detections = postprocess(output,transform,self.confidence)
        finished = perf_counter()
        return detections, {'preprocessing_ms':round((preprocessed-started)*1000,2),
            'inference_ms':round((inferred-preprocessed)*1000,2),
            'postprocessing_ms':round((finished-inferred)*1000,2)}
