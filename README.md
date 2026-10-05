# CivicEye AI

See. Detect. Prioritize. Resolve.

The existing frontend, navigation and Live Scan layout are preserved. PWA
installation uses the native browser prompt, with branded Android icons and
offline shell caching. Production builds use VITE_AI_API_URL and HTTPS.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the prepared Netlify/Render settings,
remaining account deployment actions, and validation limits.

The unchanged V2 ONNX model supports garbage and waterlogging. Automatic pothole
detection remains disabled. Pothole photo reporting is user-assisted and requires
authority review. No PyTorch, paid model API or OpenAI key is used.

This package does not mean the backend is already deployed. The packaged sample
build uses an intentionally unreachable example.invalid API origin so camera
frames cannot be sent to an unverified third-party Render hostname. Set your
actual Render HTTPS URL in VITE_AI_API_URL and rebuild before enabling live AI.

Build: npm run build. Publish directory: build. Source frontend: dist.
Offline shell and install behavior require the first successful HTTPS visit.
Actual Android installation and public Render health still need deployment checks.
