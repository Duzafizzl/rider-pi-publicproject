#!/usr/bin/env bash
# File: run_health.sh
# Description: Single test – GET /health. Then check robot/browser (stream dashboard).
# Created: 2026-02-17
# Last updated: 2026-02-17

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"

echo "→ GET $BASE/health"
curl -sf --connect-timeout 5 "$BASE/health" | python3 -m json.tool
echo ""
echo "Check: What do you see on the robot or in the browser (stream dashboard)?"
