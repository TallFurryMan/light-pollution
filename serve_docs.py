#!/usr/bin/env python3
"""Build and serve docs with the same Jekyll stack as GitHub Pages.

Requirements:
- Docker available locally.

Usage:
  python serve_docs.py

This will start a container running the GitHub Pages Jekyll image,
build the site from ./docs using the remote academicpages theme,
and serve it on http://localhost:8080.
"""

import subprocess
import sys
from pathlib import Path

IMAGE = "ghcr.io/actions/jekyll-build-pages:v1.0.13"
HOST_PORT = 8080
CONTAINER_PORT = 4000
REPO_ROOT = Path(__file__).parent.resolve()


def run_server():
    cmd = [
        "docker",
        "run",
        "--rm",
        "-p", f"{HOST_PORT}:{CONTAINER_PORT}",
        "-v", f"{REPO_ROOT}:/github/workspace",
        "-w", "/github/workspace/docs",
        IMAGE,
        "bash",
        "-lc",
        (
            "bundle exec jekyll serve "
            "--config _config.yml "
            "--destination /tmp/_site "
            "--future "
            "--host 0.0.0.0 "
            f"--port {CONTAINER_PORT}"
        ),
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Failed to start Jekyll server: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    print(f"Serving docs via Jekyll at http://localhost:{HOST_PORT}")
    run_server()
