#!/usr/bin/env bash
# File: run_snapshot.sh
# Description: Single test – GET /api/camera/snapshot, saves and opens image on this machine.
# Created: 2026-02-17
# Last updated: 2026-02-17

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"
OUT="/tmp/rider_pi_snap.jpg"

echo "→ GET $BASE/api/camera/snapshot → $OUT"
CODE=$(curl -s -o "$OUT" -w "%{http_code}" --connect-timeout 5 "$BASE/api/camera/snapshot")
if [ "$CODE" = "200" ] && [ -s "$OUT" ]; then
  echo "OK (code $CODE), image saved."
  command -v open >/dev/null 2>&1 && open "$OUT" && echo "Image opened (Mac)."
  command -v xdg-open >/dev/null 2>&1 && xdg-open "$OUT" 2>/dev/null
else
  echo "Error or empty (code $CODE)."
fi
echo ""
echo "Check: Was an image shown on this machine? (Pi LCD does not show snapshot automatically.)"
