#!/usr/bin/env bash
# File: start.sh
# Description: Starts the Rider Pi API server (rider-pi-api).
# Created: 2026-02-17
# Last updated: 2026-02-17

set -e
cd "$(dirname "$0")/.."
export HOST="${HOST:-0.0.0}"
export PORT="${PORT:-5050}"
# Use venv Python if present (same as PM2/systemd)
if [ -x ".venv/bin/python" ]; then
  exec .venv/bin/python rider_pi_server.py
else
  exec python3 rider_pi_server.py
fi
