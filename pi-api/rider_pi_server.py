#!/usr/bin/env python3
"""
rider_pi_server.py – Entry point for Rider Pi API. Starts the FastAPI app from app.main.

Created: 2026-02-17
Last updated: 2026-02-24
"""

import os

if __name__ == "__main__":
    import uvicorn
    from app.main import app

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5050"))
    uvicorn.run(app, host=host, port=port)
