#!/usr/bin/env bash
# File: test_plan_endpoints.sh
# Description: Tests API endpoints from the Rider Pi plan (Phase 1). Pi must be reachable.
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/test_plan_endpoints.sh [BASE_URL] [--no-move]
#        BASE_URL e.g. http://riderpi.local:5050 (default from RIDER_PI_HOST)
#        --no-move = no movement/resonance (read + snapshot only), robot stays still.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a

# Args: first non-option = BASE, --no-move = skip move/resonance
NO_MOVE=0
BASE=""
for a in "$@"; do
  if [ "$a" = "--no-move" ]; then NO_MOVE=1; else [ -z "$BASE" ] && [[ ! "$a" = -* ]] && BASE="$a"; fi
done
BASE="${BASE:-http://${RIDER_PI_HOST:-riderpi.local}:5050}"
BASE="${BASE%/}"

OK=0
FAIL=0
SKIPPED=0
_curl() { curl -sf --connect-timeout 5 "$BASE$1" "${@:2}"; }

echo "=== Plan-Tests: Rider Pi API ==="
echo "Base: $BASE"
[ "$NO_MOVE" -eq 1 ] && echo "Mode: --no-move (no movement, no resonance)"
echo ""

# 1. Health
echo "1. GET /health"
if _curl "/health" > /tmp/rp_health.json 2>/dev/null; then
  echo "   OK"
  grep -q '"status"' /tmp/rp_health.json && grep -q 'ok' /tmp/rp_health.json && ((OK++)) || ((FAIL++))
  cat /tmp/rp_health.json | python3 -m json.tool 2>/dev/null | head -12
else
  echo "   ERROR (Pi not reachable?)"
  ((FAIL++))
fi
echo ""

# 2. Sensors
echo "2. GET /api/sensors"
if _curl "/api/sensors" > /tmp/rp_sensors.json 2>/dev/null; then
  echo "   OK"
  ((OK++))
  cat /tmp/rp_sensors.json | python3 -m json.tool 2>/dev/null | head -10
else
  echo "   ERROR"
  ((FAIL++))
fi
echo ""

# 3. Battery
echo "3. GET /api/battery"
if _curl "/api/battery" > /tmp/rp_battery.json 2>/dev/null; then
  echo "   OK"
  ((OK++))
  cat /tmp/rp_battery.json | python3 -m json.tool 2>/dev/null
else
  echo "   ERROR"
  ((FAIL++))
fi
echo ""

# 4. Combos (sollte immer gehen)
echo "4. GET /api/combos"
if _curl "/api/combos" > /tmp/rp_combos.json 2>/dev/null; then
  echo "   OK"
  ((OK++))
  cat /tmp/rp_combos.json | python3 -m json.tool 2>/dev/null | head -15
else
  echo "   ERROR"
  ((FAIL++))
fi
echo ""

# 5. Resonance (skippable with --no-move)
echo "5. POST /api/resonance (minimal body)"
if [ "$NO_MOVE" -eq 1 ]; then
  echo "   skipped (--no-move)"
  ((SKIPPED++))
else
  CODE=$(curl -sf -o /tmp/rp_resonance.json -w "%{http_code}" --connect-timeout 5 -X POST -H "Content-Type: application/json" -d '{"pitch":0,"yaw":0,"roll":0,"duration":0.5}' "$BASE/api/resonance" 2>/dev/null || echo "000")
  if [ "$CODE" = "200" ]; then
    echo "   OK (executed)"
    ((OK++))
  elif [ "$CODE" = "503" ]; then
    echo "   OK (503 = robot not present, endpoint exists)"
    ((OK++))
  else
    echo "   Code $CODE"
    ((FAIL++))
  fi
fi
echo ""

# 6. Move (skippable with --no-move)
echo "6. POST /api/move (forward 0.3, 0.3s)"
if [ "$NO_MOVE" -eq 1 ]; then
  echo "   skipped (--no-move)"
  ((SKIPPED++))
else
  if curl -sf --connect-timeout 5 -X POST "$BASE/api/move?direction=forward&speed=0.3&duration=0.3" > /tmp/rp_move.json 2>/dev/null; then
    echo "   OK"
    ((OK++))
    cat /tmp/rp_move.json | python3 -m json.tool 2>/dev/null
  else
    echo "   ERROR"
    ((FAIL++))
  fi
fi
echo ""

# 7. Camera snapshot (may 503/500 if no camera)
echo "7. GET /api/camera/snapshot (checks endpoint)"
CODE=$(curl -s -o /tmp/rp_snap.jpg -w "%{http_code}" --connect-timeout 5 "$BASE/api/camera/snapshot" 2>/dev/null)
if [ "$CODE" = "200" ]; then
  echo "   OK (200, snapshot received)"
  ((OK++))
  if [ -f /tmp/rp_snap.jpg ] && [ -s /tmp/rp_snap.jpg ]; then
    echo "   Image: /tmp/rp_snap.jpg"
    if command -v open >/dev/null 2>&1; then
      echo "   Opening image on this machine (Mac) …"
      open /tmp/rp_snap.jpg
    elif command -v xdg-open >/dev/null 2>&1; then
      echo "   Opening image (Linux) …"
      xdg-open /tmp/rp_snap.jpg 2>/dev/null || true
    fi
  fi
elif [ "$CODE" = "503" ] || [ "$CODE" = "500" ]; then
  echo "   OK (endpoint present, camera unavailable: $CODE)"
  ((OK++))
else
  echo "   Code $CODE"
  ((FAIL++))
fi
echo ""

# 8. Faces known
echo "8. GET /api/faces/known"
if _curl "/api/faces/known" > /tmp/rp_faces.json 2>/dev/null; then
  echo "   OK"
  ((OK++))
  cat /tmp/rp_faces.json | python3 -m json.tool 2>/dev/null | head -8
else
  echo "   ERROR"
  ((FAIL++))
fi
echo ""

echo "=== Result: $OK OK, $FAIL failed${SKIPPED:+", $SKIPPED skipped (--no-move)"} ==="
[ "$FAIL" -eq 0 ] && echo "All executed plan endpoints reachable." || echo "Some calls failed (Pi/network or stub without hardware)."
