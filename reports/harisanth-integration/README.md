# Local Harisanth hybrid integration

No training, new model search, push or deployment. V2 and specialist hashes verified. All125 real image requests used the actual /detect route with 640px JPEG80 inputs; model sessions really loaded. Dedicated specialist0.35; V2 contributes only garbage/waterlogging. No stale frame cache. Same-class NMS plus near-identical cross-class conflict suppression; genuine source scores unchanged.

Pothole recall 27/28; core backgroundFP3/41; all unique backgroundFP7/64. ManholeFP4/15. Wet roadFP0/3. See report.json and real response evidence.

Mean both-model backend 604.85ms; mean ASGI roundtrip 609.18ms; p95 ASGI 638.91ms; V2-only ASGI 138.63ms. Excludes JPEG capture, physical phone/network delays. Live specialist cadence2seconds; V2 sampled on intervening requests; existing single-flight/sharpest-frame/adaptive delay and900ms stale expiry preserved. Low-confidence pothole confirmation uses class-specific3second history; skipped class requests cannot wipe it.

Garbage9/15 and waterlogging19/23 labeled-box matches, equal to actual V2-only requests. No GW detections changed in the35 positive images. These are prototype model capabilities, not perfect detection claims.

22 backend regressions pass; motion, sample cadence/generation resets, stale handling, real-response adapter/ready status, photo replacement and real-vs-demo checks pass. Local build succeeds. Browser preview failed with ERR_CONNECTION_TIMED_OUT; physical moving-camera demonstration not verified. Final health was obtained from the actual ASGI route, not a reachable TCP/browser endpoint. Safe-to-deploy gate remains false until that verification; no user production system changed.

Licenses/source cards preserved under models/pothole-specialist. Publisher MIT claim and upstream Ultralytics AGPL obligations retained. Known manhole errors documented in /health and model README.

## Deployment approval

User completed manual browser verification of pothole, garbage, waterlogging and image replacement, accepted the hackathon prototype, and explicitly authorized pushing existing main and its linked deployments. Final automated tests and model checksum/load verification pass. The earlier preview limitation is resolved by running local servers outside AppContainer isolation; no firewall setting was changed.
