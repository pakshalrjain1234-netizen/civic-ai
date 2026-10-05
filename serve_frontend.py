"""Serve the existing static app and expose public local vision configuration."""
import json
import os
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).resolve().parent


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'dist'), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if self.path.split('?')[0] == '/vision-env.js':
            config = {'production': False, 'visionApiUrl': os.getenv('VITE_AI_API_URL', 'http://127.0.0.1:8000'),
                      'frameIntervalMs': int(os.getenv('VITE_VISION_FRAME_INTERVAL_MS', '700'))}
            content = ('window.CIVICEYE_VISION_ENV = ' + json.dumps(config) + ';').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        super().do_GET()


if __name__ == '__main__':
    port = int(os.getenv('CIVICEYE_FRONTEND_PORT', '5189'))
    print(f'CivicEye frontend: http://127.0.0.1:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), FrontendHandler).serve_forever()
