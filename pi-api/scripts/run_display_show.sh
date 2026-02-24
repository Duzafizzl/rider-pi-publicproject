#!/usr/bin/env bash
# File: run_display_show.sh
# Description: Shows text on the Rider Pi LCD (POST /api/display/show). Only on Pi with xgoscreen.
# Created: 2026-02-18
# Last updated: 2026-02-24
# Usage: ./scripts/run_display_show.sh [Text]   (default: Rider Pi)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"
TEXT="${1:-Rider Pi}"

echo "→ POST $BASE/api/display/show?text=$TEXT"
curl -sf -X POST "$BASE/api/display/show?text=$TEXT" | python3 -m json.tool
echo ""
echo "Check: Do you see '$TEXT' on the display?"
