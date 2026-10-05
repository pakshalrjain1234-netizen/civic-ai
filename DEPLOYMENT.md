# CivicEye Netlify PWA + Render ONNX service

Prepared deployment, not yet published to Render or redeployed to Netlify.
The existing frontend is plain static JavaScript, not available React/Vite source.
It is preserved. The build injects the requested VITE_AI_API_URL without a rewrite.

## Render — free Python web service

Use the deployment-repository ZIP as a Git repository; its root contains render.yaml.
Create a Render Blueprint from that repository, or use these equivalent settings:

| Setting | Value |
| --- | --- |
| Runtime | Python 3.12.12 |
| Plan | Free |
| Root directory | ai-service |
| Build | pip install -r requirements.txt && python verify_model.py |
| Start | python start.py |
| Equivalent start | uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 |
| Health check | /health |

Only the approved, unchanged models/version-2/civiceye-v2.onnx is needed at runtime.
Its SHA256 is checked during the build. V1 and rejected model archives remain in the
original project; they are not loaded or uploaded in this minimal deployment bundle.
No training dependencies, PyTorch, OpenAI key or paid inference API are used.

Expected URL format: https://<assigned-service-name>.onrender.com
The sample build uses https://civiceye-ai.example.invalid, intentionally unreachable
until you rebuild with a real deployed endpoint. Use the actual HTTPS URL assigned by your Render dashboard.

CIVICEYE_CORS_ORIGINS is explicitly:

    https://dashing-speculoos-a9724c.netlify.app,http://127.0.0.1:5189,http://localhost:5189

Update the first origin if the Netlify domain changes. No wildcard and no cookies.
/health is public and reports actual model load state. ready means the supported
garbage/waterlogging service is ready; automatic_pothole_ready and pothole_detector
remain false. Live Scan explicitly labels pothole detection unavailable.

## Netlify — production build

Connect the same repository to the existing Netlify site, with base directory at
the repository root, build command npm run build and publish directory build.
Set a Builds-scoped environment variable:

    VITE_AI_API_URL=https://<actual-service-name>.onrender.com

Then redeploy. The build refuses absent, HTTP or localhost production API origins.
Existing browser-saved vision endpoints cannot override the production API origin.
For manual drag-and-drop deployment, build locally with the actual environment
variable and upload only build/. Uploading source dist/ bypasses production injection.
The provided frontend ZIP contains the unreachable example.invalid HTTPS endpoint;
rebuild with the actual Render URL before enabling detection. Environment-variable changes require a new build.

SPA refreshes use the /index.html 200 rewrite. Direct /live-scan and /login-citizen
paths are recognized in addition to existing hash routes. Assets use root paths.

## Android installation and offline behavior

Manifest: /manifest.webmanifest. Service worker: /sw.js, scope /.
Four PNG icons use the existing CivicEye eye mark, including safe-zone maskable
192 and 512 versions. Standalone, portrait-primary, CivicEye design colors.

Install CivicEye is hidden until a real beforeinstallprompt event is received.
Clicking it uses the native browser prompt; installed/standalone apps hide it.
No fake installation dialog or fabricated browser event is used in the product.

The worker caches only an explicit same-origin static startup shell. Detection,
health, API traffic, uploaded photos and user records are never worker-cached.
Offline startup works after the first successful online visit. External fonts,
maps, CDN libraries and shared account services still need network access; map
failure has the existing coordinate/manual fallback. Offline Live Scan clears
current real findings and shows AI SERVICE OFFLINE, never cached detections.

Android native installation still needs a device check after HTTPS redeployment;
browser engagement and installation availability control the native prompt.

## Remaining deployment actions

1. Publish the prepared repository to your own Git host and create the free Render service.
2. Verify its actual HTTPS /health reports model_loaded true.
3. Set the actual VITE_AI_API_URL on Netlify and rebuild/redeploy.
4. Open the updated HTTPS site in Android Chrome and check native installation.

These actions have not been performed against your hosting accounts. The old
Netlify deployment remains unchanged until you redeploy these artifacts.
Render Free sleeps after 15 idle minutes and a cold start can take about a minute;
Live Scan stays honestly offline/retrying until the service is available.
This is a free prototype deployment, without an always-on production availability claim.

Official references:
- https://render.com/docs/free
- https://render.com/docs/health-checks
- https://render.com/docs/blueprint-spec
- https://docs.netlify.com/configure-builds/environment-variables
- https://docs.netlify.com/manage/routing/redirects/redirect-options/
- https://web.dev/articles/install-criteria
- https://web.dev/articles/customize-install
