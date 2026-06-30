#!/usr/bin/env python3
"""
Simple dev proxy server.
Serves static files from `frontend/` and proxies requests starting with /api to backend at http://127.0.0.1:5000

Run: python dev_proxy.py
"""
import http.server
import socketserver
import requests
import urllib.parse
import os
import sys

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
BACKEND_BASE = 'http://127.0.0.1:5000'
PORT = 5000


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _proxy_request(self):
        method = self.command
        # Build backend URL
        url = BACKEND_BASE + self.path

        # Prepare headers (exclude hop-by-hop headers)
        headers = {k: v for k, v in self.headers.items() if k.lower() not in (
            'host', 'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization',
            'te', 'trailers', 'transfer-encoding', 'upgrade')}

        data = None
        if 'content-length' in (k.lower() for k in self.headers.keys()):
            try:
                length = int(self.headers.get('Content-Length'))
                data = self.rfile.read(length) if length > 0 else None
            except Exception:
                data = None

        try:
            resp = requests.request(method, url, headers=headers, data=data, params=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query), timeout=30)

            # Send status
            self.send_response(resp.status_code)

            # Copy headers from backend response (skip hop-by-hop)
            for k, v in resp.headers.items():
                if k.lower() in ('content-encoding', 'transfer-encoding', 'connection'):
                    continue
                # Allow Set-Cookie to pass through
                self.send_header(k, v)
            self.end_headers()

            # Write body
            if resp.content:
                self.wfile.write(resp.content)

        except requests.exceptions.RequestException as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        if self.path.startswith('/api'):
            self._proxy_request()
        else:
            return super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api'):
            self._proxy_request()
        else:
            return super().do_POST()

    def do_PUT(self):
        if self.path.startswith('/api'):
            self._proxy_request()
        else:
            return super().do_PUT()

    def do_DELETE(self):
        if self.path.startswith('/api'):
            self._proxy_request()
        else:
            return super().do_DELETE()


def run(server_class=http.server.ThreadingHTTPServer, handler_class=ProxyHandler):
    os.chdir(FRONTEND_DIR)
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Serving frontend from {FRONTEND_DIR} on http://127.0.0.1:{PORT}")
    print(f"Proxying /api -> {BACKEND_BASE}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        httpd.server_close()


if __name__ == '__main__':
    run()
