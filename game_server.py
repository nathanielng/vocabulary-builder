#!/usr/bin/env python3
"""
Vocabulary Builder Game Server
Run:  python game_server.py
Open: http://localhost:8080
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PROGRESS_FILE = "data/progress.json"
PORT = 8080


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            try:
                with open("data/misspellings.json") as f:
                    self._json(200, json.load(f))
            except FileNotFoundError:
                self._json(404, {"error": "misspellings.json not found. Run generate_misspellings.py first."})
        elif path == "/api/progress":
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE) as f:
                    self._json(200, json.load(f))
            else:
                self._json(200, {})
        elif path == "/":
            self.path = "/game_word_drop.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/progress":
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            os.makedirs("data", exist_ok=True)
            with open(PROGRESS_FILE, "w") as f:
                json.dump(json.loads(body), f, indent=2)
            self._json(200, {"ok": True})
        else:
            self._json(404, {"error": "not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # suppress per-request noise


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print("Vocabulary Builder Games")
    print(f"  Word Drop:  http://localhost:{PORT}/game_word_drop.html")
    print(f"  Spelling:   http://localhost:{PORT}/game_spelling.html")
    print("Press Ctrl+C to quit.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
