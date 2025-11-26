#!/usr/bin/env python3
"""Simple HTTP server to serve the `docs` folder.

This script is intended for quick local documentation browsing.
After installing the repository, run:

```bash
python serve_docs.py
```

A web page will be available at http://localhost:8000.
"""

import http.server
import socketserver
import urllib.parse
import pathlib
import os

PORT = 8000
DOCS_DIR = pathlib.Path(__file__).parent / "docs"

# Serve docs with language-aware paths (/en, /fr).
class DocsHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        parsed = urllib.parse.urlparse(path).path
        # Normalize to strip leading slashes
        if parsed.startswith("/en/"):
            root = DOCS_DIR / "en"
            rel = parsed[len("/en/") :]
        elif parsed.startswith("/fr/"):
            root = DOCS_DIR / "fr"
            rel = parsed[len("/fr/") :]
        else:
            root = DOCS_DIR
            rel = parsed.lstrip("/")
        full = (root / rel).resolve()
        return str(full)

    def end_headers(self):
        # Allow cross‑origin requests during local browsing.
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format, *args):
        # Silence the default stdout logs.
        return

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DocsHandler) as httpd:
        print(f"Serving docs at http://localhost:{PORT}")
        httpd.serve_forever()
