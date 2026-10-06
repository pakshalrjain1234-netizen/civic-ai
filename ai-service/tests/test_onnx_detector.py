"""Numerical/metadata test fixtures only; no model file or live detections created."""
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image
from utils.detector import CivicDetector, letterbox_tensor, postprocess, raw_predictions, ONNX_FORMAT

def output(rows):
    values=np.zeros((1,7,8400),dtype=np.float32)
    for i,row in enumerate(rows):values[0,:,i]=row
    return values

class OnnxTests(unittest.TestCase):
    def test_letterbox_colors_dtype_and_odd_padding(self):
        tensor,transform=letterbox_tensor(Image.new('RGB',(1000,501),(255,0,0)))
        self.assertEqual(tensor.shape,(1,3,640,640));self.assertEqual(tensor.dtype,np.float32)
        self.assertEqual(transform[:3],(.64,0,159))
        np.testing.assert_allclose(tensor[0,:,320,320],[1,0,0])
        np.testing.assert_allclose(tensor[0,:,0,0],[114/255]*3)

    def test_original_coordinates_class_aware_nms_and_filter(self):
        values=output([[320,320,320,160,.9,.1,.2],[321,320,320,160,.8,.1,.2],
                       [320,320,320,160,.1,.85,.1],[100,200,30,30,.1,.1,.2]])
        results=postprocess(values,(.64,0,160,1000,500))
        self.assertEqual([r['class'] for r in results],['pothole','garbage'])
        self.assertAlmostEqual(results[0]['bbox']['x'],.25);self.assertAlmostEqual(results[0]['bbox']['y'],.25)
        self.assertAlmostEqual(results[0]['bbox']['width'],.5);self.assertAlmostEqual(results[0]['bbox']['height'],.5)
        self.assertEqual(results[0]['confidence'],.9)
        self.assertEqual(results,postprocess(values.transpose(0,2,1),(.64,0,160,1000,500)))

    def test_empty_invalid_and_padding_only_predictions(self):
        self.assertEqual(postprocess(output([]),(1,0,0,640,640)),[])
        self.assertEqual(postprocess(output([[100,50,20,20,.9,0,0]]),(.64,0,160,1000,500)),[])
        with self.assertRaises(ValueError):raw_predictions(np.zeros((1,6,100),dtype=np.float32))
        bad=output([]);bad[0,0,0]=np.nan
        with self.assertRaises(ValueError):raw_predictions(bad)

    def session(self):
        session=MagicMock()
        session.get_modelmeta.return_value=SimpleNamespace(custom_metadata_map={'names':json.dumps({0:'pothole',1:'garbage',2:'waterlogging'}),'task':'detect','civiceye_format':ONNX_FORMAT})
        session.get_inputs.return_value=[SimpleNamespace(name='images',type='tensor(float)',shape=[1,3,640,640])]
        session.get_outputs.return_value=[SimpleNamespace(name='output0',type='tensor(float)',shape=[1,7,8400])]
        session.run.return_value=[output([])]
        return session

    def test_load_metadata_and_real_run_gate(self):
        session=self.session();detector=CivicDetector(Path('test-only-not-saved.onnx'))
        with patch.object(Path,'is_file',return_value=True),patch('onnxruntime.InferenceSession',return_value=session):
            detector.load();self.assertIs(detector.model,session);session.run.assert_called_once()
            session.get_modelmeta.return_value.custom_metadata_map['names']="{0:'garbage',1:'pothole',2:'waterlogging'}"
            detector.load();self.assertIsNone(detector.model)
            self.assertIn('Incorrect CivicEye weights',detector.error)
            session.get_modelmeta.return_value.custom_metadata_map['names']="{0:'pothole',1:'garbage',2:'waterlogging'}"
            session.run.side_effect=RuntimeError('Runtime warm-up failure')
            detector.load();self.assertIsNone(detector.model)

    def test_no_pytorch_or_ultralytics_imports(self):
        self.assertNotIn('torch',sys.modules);self.assertNotIn('ultralytics',sys.modules)

if __name__=='__main__':unittest.main()
