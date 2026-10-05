# CivicEye Colab preparation — current status

| Split | Total | Real positives | Real negatives | Synthetic | Real pothole | Real garbage | Real waterlogging |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 828 | 555 | 70 | 203 | 171 | 244 | 140 |
| val | 171 | 151 | 20 | 0 | 46 | 65 | 40 |
| test | 76 | 66 | 10 | 0 | 16 | 30 | 20 |

1,075 images: 772 real positives (233 pothole, 339 garbage, 200 waterlogging), 100 real negatives, 203 synthetic. 42 RDD images / 66 boxes removed, including 17 clear cases and 25 conservatively withheld ambiguous cases. Excluded originals preserved separately. All file/label/provenance checks pass; zero cross-split duplicate candidates. No split reshuffling. No training occurred. See ../../CivicEye_Colab_Guide.md and ../../CivicEye_YOLO_Training_Colab.ipynb.

Local Windows PyTorch blocking still applies to inference. The notebook runs on your Colab runtime; no security protections were changed. Frontend and Live Scan are unchanged.
