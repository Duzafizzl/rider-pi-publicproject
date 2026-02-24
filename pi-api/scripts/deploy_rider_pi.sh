#!/usr/bin/env bash
# File: deploy_rider_pi.sh
# Description: Rsync this project to the Rider Pi (~/rider-pi-api), then create a Git commit on the Pi as rollback point.
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: from project root: ./scripts/deploy_rider_pi.sh [user@host]
# Loads config/.env if present (RIDER_PI_HOST). Optional: RIDER_PI_PASSWORD for sshpass; otherwise SSH will prompt.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
TARGET="${1:-pi@${RIDER_PI_HOST:-riderpi.local}}"
[[ "$TARGET" != *@* ]] && TARGET="pi@${TARGET}"
RSYNC_EXCLUDE="--exclude=.venv --exclude=__pycache__ --exclude=.git --exclude=*.pyc --exclude=logs/*.log"

if command -v sshpass >/dev/null 2>&1 && [ -n "${RIDER_PI_PASSWORD}" ]; then
  RSYNC_SSH="sshpass -p \"$RIDER_PI_PASSWORD\" ssh -o StrictHostKeyChecking=accept-new"
  SSH_CMD() { sshpass -p "$RIDER_PI_PASSWORD" ssh -o StrictHostKeyChecking=accept-new "$TARGET" "$@"; }
else
  RSYNC_SSH="ssh -o StrictHostKeyChecking=accept-new"
  SSH_CMD() { ssh -o StrictHostKeyChecking=accept-new "$TARGET" "$@"; }
fi

echo "STEP 1: Deploy $ROOT -> $TARGET:rider-pi-api/"
rsync -avz -e "$RSYNC_SSH" $RSYNC_EXCLUDE "$ROOT/" "$TARGET:rider-pi-api/"
echo "STEP 2: Creating Git rollback point on the Pi..."
SSH_CMD 'bash -s' < "$ROOT/scripts/pi_git_commit.sh"
echo "Done. On the Pi: cd rider-pi-api && ./scripts/start.sh  or  pm2 restart rider-pi-api  or  sudo systemctl restart rider-pi-api"
