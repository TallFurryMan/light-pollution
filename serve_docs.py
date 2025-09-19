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
import os
import pathlib

PORT = 8000
DOCS_DIR = pathlib.Path(__file__).parent / "docs"

# Serve the pre‑generated index.html that renders the markdown files.
class DocsHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS_DIR), **kwargs)

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
