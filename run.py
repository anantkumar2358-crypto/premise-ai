#!/usr/bin/env python3
"""
Entry point to launch Premise Web Application Server.
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import socket

def find_open_port(start_port=8000, max_port=8090):
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return 8080

if __name__ == "__main__":
    port = int(os.environ.get("PORT", find_open_port(8000)))
    print("\n" + "=" * 65)
    print("  🛡️  PREMISE: Blind Spot & Assumption Intelligence Engine")
    print("=" * 65)
    print(f"  Server starting at: http://localhost:{port}")
    print(f"  Interactive API docs: http://localhost:{port}/docs")
    print("=" * 65 + "\n")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
