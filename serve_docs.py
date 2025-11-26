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
import os

PORT = 8000
# Default to French docs; can override with DOCS_LANG=en
LANG = os.environ.get("DOCS_LANG", "fr")
base_dir = pathlib.Path(__file__).parent / "docs"
DOCS_DIR = base_dir / LANG if (base_dir / LANG).exists() else base_dir

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
