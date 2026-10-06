"""Metric regressions only: these synthetic rows are never model detections."""
import unittest
from training.evaluate_pothole_specialist import average_precision, overlap

class PotholeEvaluationTests(unittest.TestCase):
    def test_perfect_detection_has_high_ap_at_every_iou(self):
        ap=average_precision([(.9,[True]*10),(.8,[True]*10)],2)
        self.assertTrue(all(.99 <= value <= 1 for value in ap))

    def test_high_confidence_false_positive_reduces_ap(self):
        perfect=average_precision([(.8,[True]*10)],1)
        false_first=average_precision([(.9,[False]*10),(.8,[True]*10)],1)
        self.assertTrue(all(b < a for a,b in zip(perfect,false_first)))

    def test_missed_ground_truth_reduces_ap(self):
        ap=average_precision([(.9,[True]*10)],2)
        self.assertTrue(all(value < .6 for value in ap))

    def test_strict_iou_does_not_reuse_loose_match(self):
        ap=average_precision([(.9,[True]*5+[False]*5)],1)
        self.assertGreater(ap[0],.99)
        self.assertEqual(ap[-1],0)

    def test_empty_cases_and_geometry(self):
        self.assertEqual(average_precision([],1),[0]*10)
        self.assertEqual(average_precision([(.9,[False]*10)],0),[0]*10)
        self.assertEqual(overlap([0,0,1,1],[0,0,1,1]),1)
        self.assertEqual(overlap([0,0,.1,.1],[.5,.5,1,1]),0)
