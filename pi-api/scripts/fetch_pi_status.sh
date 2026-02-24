#!/usr/bin/env bash
# File: fetch_pi_status.sh
# Description: Fetch current status from Rider Pi (run once; enter SSH password if prompted).
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/fetch_pi_status.sh   (or: bash scripts/fetch_pi_status.sh)

# Target: pi@riderpi.local (set RIDER_PI_HOST; optional RIDER_PI_PASSWORD for sshpass)
TARGET="${1:-pi@${RIDER_PI_HOST:-riderpi.local}}"
OUTPUT="${2:-./docs/pi_status_$(date +%Y%m%d_%H%M).txt}"

echo "Connecting to $TARGET and writing status to $OUTPUT ..."
ssh "$TARGET" 'echo "=== Host ===" && hostname && uname -a && echo "" && echo "=== User/Home ===" && whoami && echo $HOME && ls -la ~ && echo "" && echo "=== rider-pi-api ===" && (ls -laR ~/rider-pi-api 2>/dev/null || echo "Folder ~/rider-pi-api not found") && echo "" && echo "=== Python ===" && python3 --version 2>/dev/null && which python3 && echo "" && echo "=== pip list ===" && pip3 list 2>/dev/null && echo "" && echo "=== Port 5050 ===" && (ss -tlnp 2>/dev/null | grep 5050 || netstat -tlnp 2>/dev/null | grep 5050 || echo "Port 5050 not in use")' | tee "$OUTPUT"
echo ""
echo "Done. Output in: $OUTPUT"
