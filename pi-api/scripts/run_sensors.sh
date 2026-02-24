#!/usr/bin/env bash
# File: run_sensors.sh
# Description: Single test – GET /api/sensors (battery, attitude).
# Created: 2026-02-17
# Last updated: 2026-02-17

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"

echo "→ GET $BASE/api/sensors"
curl -sf --connect-timeout 5 "$BASE/api/sensors" | python3 -m json.tool
echo ""
echo "Check: Does the display (battery, tilt) match the robot?"
