#!/usr/bin/env bash
# File: run_led.sh
# Description: Single test – POST /api/led (RGB LED on robot).
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/run_led.sh [r] [g] [b]   (default: 128 0 255 = purple)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"
R="${1:-128}"
G="${2:-0}"
B="${3:-255}"

echo "→ POST $BASE/api/led (r=$R g=$G b=$B)"
curl -sf --connect-timeout 5 -X POST "$BASE/api/led?r=$R&g=$G&b=$B" | python3 -m json.tool
echo ""
echo "Check: Is the LED showing the expected color?"
