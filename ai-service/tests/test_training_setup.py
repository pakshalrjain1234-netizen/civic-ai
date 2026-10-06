import sys
from pathlib import Path
import unittest
import tempfile
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'training'))
from common import prepare_dataset, validate_label_line
from utils.classes import CLASS_NAMES, validate_class_names


class TrainingSetupTests(unittest.TestCase):
    def test_exact_class_mapping(self):
        self.assertEqual(validate_class_names(CLASS_NAMES), CLASS_NAMES)
        for names in ({0:'garbage',1:'pothole',2:'waterlogging'}, {**CLASS_NAMES,3:'road'}, ['pothole','garbage']):
            with self.assertRaises(ValueError):
                validate_class_names(names)

    def test_invalid_annotations_are_rejected(self):
        for line in ('3 .5 .5 .2 .2','0 10 20 30 40','1 .5 .5 0 .2','2 nan .5 .1 .1','0 .95 .5 .5 .1','1 .5 .5 .2 .2 .9'):
            with self.assertRaises(ValueError):
                validate_label_line(line)

    def test_empty_dataset_refuses_training(self):
        # No images or labels are created by this test.
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / 'dataset.yaml'
            config.write_text(yaml.safe_dump({'path': str(Path(temporary) / 'empty'), 'nc': 3, 'names': CLASS_NAMES, 'train': 'images/train', 'val': 'images/val'}))
            with self.assertRaisesRegex(ValueError, 'No real images'):
                prepare_dataset(config)


if __name__ == '__main__':
    unittest.main()
