import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from utils.hybrid import HybridDetector, merge_detections
class HybridTests(unittest.TestCase):
 def test_missing_specialist_preserves_v2(self):
  with TemporaryDirectory(dir='../../../work') as directory:
   d=HybridDetector(Path(directory));d.local.load=lambda: setattr(d.local,'model',object());d.load()
   self.assertTrue(d.health()['garbage_waterlogging_detector']);self.assertFalse(d.health()['pothole_detector'])
 def test_requires_actual_session(self):
  d=HybridDetector(Path('.'));d.accepted=True;self.assertFalse(d.health()['pothole_detector'])
 def test_v2_only_does_not_run_specialist(self):
  d=HybridDetector(Path('.'));d.accepted=True;d.pothole.model=object();d.local.detect_profiled=lambda im:([],{})
  d.pothole.detect=lambda im:self.fail('Skipped specialist ran');self.assertEqual(d.detect(None,False),[])
 def test_merge_duplicates_and_conflicts_keeps_nested(self):
  a={'class':'pothole','confidence':.8,'bbox':{'x':0,'y':0,'width':1,'height':1}}
  b={**a,'confidence':.7};c={**a,'class':'waterlogging','confidence':.6}
  self.assertEqual(merge_detections([b,c,a]),[a])
  c={**c,'bbox':{'x':0,'y':0,'width':.3,'height':.3}}
  self.assertEqual(len(merge_detections([a,c])),2)
