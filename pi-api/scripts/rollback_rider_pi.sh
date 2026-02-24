#!/usr/bin/env bash
# File: rollback_rider_pi.sh
# Description: Rollback on the Rider Pi to a previous deploy (tag or commit).
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/rollback_rider_pi.sh [user@host] <tag or commit>
# Example: ./scripts/rollback_rider_pi.sh pi@riderpi.local deploy-20260217-141500
#          ./scripts/rollback_rider_pi.sh pi@riderpi.local HEAD~1

TARGET="${1:-pi@${RIDER_PI_HOST:-riderpi.local}}"
REF="${2:?Missing: tag or commit (e.g. deploy-20260217-141500 or HEAD~1)}"

echo "Rollback on Pi ($TARGET) to: $REF"
ssh "$TARGET" "cd ~/rider-pi-api && git status && git log --oneline -3 && git reset --hard $REF && echo 'Rollback done.' && git log --oneline -1"
