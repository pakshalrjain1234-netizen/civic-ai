# Live Scan and role logins

The existing application has been extended in place. Citizen reporting, authority administration, worker repair, and before/after review remain available.

## Demo credentials

| Role | Email | Password | Screen |
|---|---|---|---|
| Citizen | citizen@civiceye.demo | Citizen@123 | #login-citizen |
| Authority | authority@civiceye.demo | Authority@123 | #login-authority |
| Field worker | worker@civiceye.demo | Worker@123 | #login-worker |

Use the role tabs, then **Use demo credentials** and **Sign in to demo**. Wrong-role credentials are rejected. These credentials work only in the local demo; they do not create Supabase users or grant real privileges. Live login continues to use Supabase Auth and administrator-managed roles.

## Local Python vision integration

The default connection now uses a local FastAPI service at http://127.0.0.1:8000. It checks /health, posts compressed frames to /detect at a 700 ms target interval, and draws normalized boxes using a transparent responsive canvas. Missing weights display AI SERVICE CONNECTED — MODEL NOT LOADED. See [ai-service/README.md](ai-service/README.md). This supersedes the earlier Supabase fallback scanning cadence described below; image reporting and verification still use their existing Supabase function.

## Live camera scanning

Citizen and authority navigation includes Live Scan. DriveScan uses the same camera, response validation, frame scheduling, and incident handoff. Uploading video remains supported.

Start / stop / switch camera, pause / resume analysis, rear-camera preference, location capture, normalized bounding-box overlays, timestamped detection feed, and manual incident creation are implemented. Frames are compressed to JPEG with a maximum dimension of 1024 pixels. Detection requests are serialized. The configurable external-detector interval is 750 ms; slower requests reduce actual frequency automatically. Supabase's existing general-purpose image-analysis function is sampled at 10.5 seconds to respect its rate limit and does not return bounding boxes or coverage. Use a trained detection endpoint for the requested fast object-localization workflow.

No model connected means **AI MODEL NOT CONNECTED**, with no generated findings. Demo Mode is separate, explicitly labeled, and displays only user-staged sample findings. An empty successful detector response displays **NO CIVIC ISSUE DETECTED**.

## Endpoint contract

In Connections, save the HTTPS vision endpoint, for example your own `/api/vision/detect` service. Localhost HTTP is permitted for development. No detector is hosted by this static app; the integration expects a connected real service. Do not put provider secrets in the browser. The endpoint must allow the site's browser origin via CORS.

Request:

```json
{"image":"data:image/jpeg;base64,...","timestamp":"2026-10-02T10:00:00Z","frame":{"coordinates":"normalized"}}
```

Response:

```json
{"detections":[{"class":"waterlogging","confidence":0.91,"bbox":{"x":0.2,"y":0.3,"width":0.4,"height":0.3},"severity":"high","surfaceCoverage":52,"explanation":"Standing water is visible on the road."}]}
```

Classes are `pothole`, `garbage`, or `waterlogging`; confidence is 0–1; bounding boxes use normalized coordinates relative to the exact submitted image. Return `{"detections":[]}` for no issue. Missing bounding boxes are disclosed, never invented. If supplied, surfaceCoverage must be 0–100 and mean estimated visual region coverage, not water depth.

Prototype coverage thresholds: ≤15 LOW; >15–35 MEDIUM; >35–<60 HIGH; ≥60 CRITICAL. No exact physical dimensions or depth are inferred. The server should document which visible road/region forms the coverage denominator.

The feed suppresses same-class entries for ten seconds and retains the highest-confidence frame during that interval. This is coarse temporal suppression, not multi-object tracking or geographic deduplication. No incident is created until a user selects a finding, adds location, reviews it, and submits through the existing duplicate workflow.

## Supabase integration

Apply `supabase/scan-context.sql` after the two existing schema scripts. It adds optional scan metadata to incident_reports, without changing existing routing or authorization. Captured time, source confidence, visual severity, and estimated coverage are saved alongside the user's report. If an external detector is used with Live Supabase Mode, the selected image is confirmed by the existing server-side analyze-image function before incident creation. The database accepts canonical analysis evidence only; arbitrary external endpoint output cannot bypass server validation.

## Validation

All three demo login screens were tested for incorrect credentials and correct-dashboard access. Live Scan was tested with a browser test camera and a mocked vision endpoint: disconnected behavior, normalized overlays, water severity thresholds, serialized requests, repeated-frame suppression, incident handoff, and mobile layout. The existing report-to-repair regression flow still passes. Real physical cameras and trained detector behavior require testing on the user's hardware and connected service.
