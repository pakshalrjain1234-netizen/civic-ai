"""Local raw YOLO ONNX pothole boxes. Mask coefficients are never class scores.

The segmentation adapter uses its genuine detection head only, not mask-to-box
conversion. Normal inference imports neither torch nor network libraries.
"""
import ast
import json
from pathlib import Path
from .detector import letterbox_tensor, postprocess


class PotholeDetector:
    def __init__(self, model_path, confidence=.35, class_index=0, class_count=1, image_size=640, mask_channels=0):
        self.model_path = Path(model_path)
        self.confidence = confidence
        self.class_index, self.class_count = class_index, class_count
        self.image_size, self.mask_channels = image_size, mask_channels
        self.model = None; self.error = None

    def _validate_output(self, output):
        import numpy as np
        if output.ndim != 3 or output.shape[0] != 1:
            raise ValueError('Expected batch-one raw pothole output.')
        channels = 4 + self.class_count + self.mask_channels
        if output.shape[1] == channels and output.shape[2] > channels:
            raw = output
        elif output.shape[2] == channels and output.shape[1] > channels:
            raw = output.transpose(0, 2, 1)
        else:
            raise ValueError('Expected xywh plus documented class probabilities, without embedded NMS.')
        scores = raw[:,4:4+self.class_count]
        if not np.isfinite(raw).all() or np.any(scores < 0) or np.any(scores > 1):
            raise ValueError('Invalid pothole probabilities.')
        return raw

    def load(self):
        self.model = None; self.error = None
        try:
            import numpy as np
            import onnxruntime as ort
            if not self.model_path.is_file():
                raise ValueError('Validated local pothole ONNX model is not installed.')
            options = ort.SessionOptions(); options.intra_op_num_threads = 2
            session = ort.InferenceSession(str(self.model_path), sess_options=options,
                                           providers=['CPUExecutionProvider'])
            inputs, outputs = session.get_inputs(), session.get_outputs()
            meta = session.get_modelmeta().custom_metadata_map
            names = ast.literal_eval(meta.get('names', '{}'))
            if meta.get('task') != ('segment' if self.mask_channels else 'detect') or len(names) != self.class_count or not 0 <= self.class_index < self.class_count:
                raise ValueError('Model class count does not match the documented pothole source.')
            if self.class_count > 1 and str(names.get(self.class_index, names.get(str(self.class_index), ''))).lower() != 'pothole':
                raise ValueError('Only the documented pothole class may be imported.')
            if len(inputs) != 1 or inputs[0].type != 'tensor(float)' or inputs[0].shape != [1,3,self.image_size,self.image_size]:
                raise ValueError(f'Expected static float32 input [1,3,{self.image_size},{self.image_size}].')
            if len(outputs) != (2 if self.mask_channels else 1) or outputs[0].type != 'tensor(float)':
                raise ValueError('Expected one raw detection output.')
            self.input_name, self.output_name = inputs[0].name, outputs[0].name
            self._validate_output(session.run([self.output_name],
                {self.input_name: np.zeros((1,3,self.image_size,self.image_size), dtype=np.float32)})[0])
            self.model = session
        except Exception as exc:
            self.error = str(exc) if isinstance(exc, ValueError) else 'Local pothole ONNX model could not load.'

    def detect(self, image):
        import numpy as np
        if self.model is None:
            raise RuntimeError(self.error or 'Pothole ONNX model is not loaded.')
        tensor, transform = letterbox_tensor(image, self.image_size)
        output = self._validate_output(self.model.run([self.output_name], {self.input_name:tensor})[0])
        # Reuse the already verified geometry/NMS implementation. The two unused
        # class scores are zero; only the source model's real pothole score is used.
        padded = np.zeros((1,7,output.shape[2]), dtype=np.float32)
        padded[:,:4] = output[:,:4]
        scores = output[:,4:4+self.class_count]
        # All unrelated road-distress classes are filtered, never reclassified.
        padded[:,4] = np.where(scores.argmax(axis=1) == self.class_index,
                              scores[:,self.class_index], 0)
        return [{**d, 'detector':'pothole-specialist'} for d in
                postprocess(padded, transform, self.confidence) if d['class'] == 'pothole']
