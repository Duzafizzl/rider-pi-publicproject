#!/usr/bin/env bash
# File: smoke_test_pi.sh
# Description: Quick test of Rider Pi API from your PC (health + sensors). Pi server must be running.
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/smoke_test_pi.sh   (from project root, loads config/.env)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="${RIDER_PI_BASE_URL:-http://${RIDER_PI_HOST:-riderpi.local}:5050}"
BASE="${BASE%/}"

echo "=== Smoke Test Rider Pi API ==="
echo "Base URL: $BASE"
echo ""

echo "1. GET /health"
if curl -sf "$BASE/health" > /tmp/rider_pi_health.json 2>/dev/null; then
  echo "   OK"
  cat /tmp/rider_pi_health.json | python3 -m json.tool 2>/dev/null || cat /tmp/rider_pi_health.json
else
  echo "   ERROR (Pi server not running or not reachable?)"
  exit 1
fi
echo ""

echo "2. GET /api/sensors"
if curl -sf "$BASE/api/sensors" > /tmp/rider_pi_sensors.json 2>/dev/null; then
  echo "   OK"
  cat /tmp/rider_pi_sensors.json | python3 -m json.tool 2>/dev/null || cat /tmp/rider_pi_sensors.json
else
  echo "   ERROR or stub (robot_available: false)"
  cat /tmp/rider_pi_sensors.json 2>/dev/null || true
fi
echo ""

echo "=== Smoke test done ==="
