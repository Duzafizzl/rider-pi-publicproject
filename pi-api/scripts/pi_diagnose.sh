#!/usr/bin/env bash
# File: pi_diagnose.sh
# Description: Via SSH: query processes, port 5050, PM2, logs, health from Rider Pi (display content not readable).
# Created: 2026-02-17
# Last updated: 2026-02-17
# Usage: ./scripts/pi_diagnose.sh   (loads config/.env for RIDER_PI_HOST, optional RIDER_PI_PASSWORD)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
TARGET="pi@${RIDER_PI_HOST:-riderpi.local}"

_run() {
  if command -v sshpass >/dev/null 2>&1 && [ -n "${RIDER_PI_PASSWORD}" ]; then
    sshpass -p "$RIDER_PI_PASSWORD" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$TARGET" "$@"
  else
    ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=8 "$TARGET" "$@"
  fi
}

echo "=== Rider Pi diagnose: $TARGET ==="
_run 'echo "--- Processes (rider-pi-api/uvicorn/python) ---"; ps aux | grep -E "rider-pi-api|rider_pi|uvicorn" | grep -v grep; echo ""; echo "--- Port 5050 ---"; ss -tlnp 2>/dev/null | grep 5050 || true; echo ""; echo "--- PM2 ---"; (pm2 list 2>/dev/null || true); echo ""; echo "--- Last 15 lines server.log ---"; tail -15 ~/rider-pi-api/logs/server.log 2>/dev/null || echo "No server.log"; echo ""; echo "--- Health (localhost:5050) ---"; curl -sf --connect-timeout 2 http://127.0.0.1:5050/health 2>/dev/null || echo "not reachable"'
echo ""
echo "=== Done (display content cannot be read via SSH – check physically if needed) ==="
