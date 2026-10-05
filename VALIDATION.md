# Validation

Checked 2 October 2026.

Passed in a real headless Edge browser:

- Citizen photo report with explicit simulated detection.
- Authority assignment appears in worker tasks.
- Assigned → Accepted → En Route → On Site → In Progress.
- New after-repair image → simulated visual verification → Resolved.
- Duplicate within 40 m merges support into the original incident.
- Worker navigation cannot open authority administration.
- 390 × 844 mobile viewport without horizontal page overflow.
- No browser JavaScript runtime errors in the tested flow.

Passed against a local PostgreSQL-compatible PGlite runtime:

- Both initial Supabase SQL scripts parse and apply.
- Citizen cannot assign workers or promote their role.
- Unassigned account cannot accept another worker's task.
- Assigned worker sees the original evidence and advances valid statuses.
- Report and completion images must match their server-side analysis.
- Valid server-recorded after-image analysis resolves the database incident.

Not yet verified against external services: Supabase Auth email delivery, deployed Storage and Edge Function execution, live vision model behavior on the physical miniature, GPS/camera permissions on the user's phone, cross-device synchronization, and supported-browser WebMCP execution. These require the user's project configuration.

Local Python integration: five API tests passed for health/missing weights, image decoding, bounded uploads, CORS, and inference serialization with responsive health checks. Browser tests passed for real missing-model health, no inference uploads before readiness, canvas resizing, serialized frame uploads, spatial duplicate suppression, and service offline handling. Detection-ready responses in browser tests were test fixtures; actual YOLO predictions were not run without trained weights.
