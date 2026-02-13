#!/usr/bin/env python3
"""Entry point for Railway deployment - handles PORT env var properly."""
import os
import sys
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}", file=sys.stderr)
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
