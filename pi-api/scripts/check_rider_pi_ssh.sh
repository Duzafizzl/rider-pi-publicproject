#!/usr/bin/env bash
# File: check_rider_pi_ssh.sh
# Description: Checks via SSH the folder structure and state of ~/rider-pi-api on the Rider Pi.
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/check_rider_pi_ssh.sh [user@host]
#        Loads config/.env if present (RIDER_PI_HOST; optional RIDER_PI_PASSWORD for sshpass).

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
TARGET="${1:-pi@${RIDER_PI_HOST:-riderpi.local}}"
# If only host given, use pi@
[[ "$TARGET" != *@* ]] && TARGET="pi@${TARGET}"

_run() {
  if command -v sshpass >/dev/null 2>&1 && [ -n "${RIDER_PI_PASSWORD}" ]; then
    sshpass -p "$RIDER_PI_PASSWORD" ssh -o StrictHostKeyChecking=accept-new "$TARGET" "$@"
  else
    ssh -o StrictHostKeyChecking=accept-new "$TARGET" "$@"
  fi
}

echo "=== Check Rider Pi: $TARGET ==="
echo ""

_run 'echo "--- /home/pi (excerpt) ---" && ls -la ~ | head -22'
echo ""

_run 'echo "--- ~/rider-pi-api (root) ---" && (ls -la ~/rider-pi-api 2>/dev/null || echo "ERROR: ~/rider-pi-api not found")'
echo ""

_run 'echo "--- ~/rider-pi-api/scripts ---" && (ls -la ~/rider-pi-api/scripts 2>/dev/null || echo "ERROR: scripts not found")'
echo ""

_run 'echo "--- ~/rider-pi-api app/config/data ---" && (ls ~/rider-pi-api/app 2>/dev/null; ls ~/rider-pi-api/config 2>/dev/null; ls ~/rider-pi-api/data 2>/dev/null)'
echo ""

_run 'echo "--- Git (rider-pi-api) ---" && (cd ~/rider-pi-api && git status -sb 2>/dev/null && git log --oneline -3 2>/dev/null) || echo "No Git or error"'
echo ""

_run 'echo "--- Deploy scripts present? ---" && (ls ~/rider-pi-api/scripts/deploy_rider_pi.sh ~/rider-pi-api/scripts/rollback_rider_pi.sh 2>/dev/null && echo "OK") || echo "ERROR: deploy_rider_pi.sh or rollback_rider_pi.sh missing"'
echo ""

echo "=== Check done ==="
