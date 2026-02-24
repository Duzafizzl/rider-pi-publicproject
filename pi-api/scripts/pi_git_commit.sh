#!/usr/bin/env bash
# File: pi_git_commit.sh
# Description: Runs on the Pi in ~/rider-pi-api: saves current state as Git commit (rollback point).
# Created: 2026-02-17
# Last updated: 2026-02-24
# Called via SSH by the deploy script; do not run directly on your Mac.

set -e
command -v git >/dev/null || { echo "Git not installed on Pi – skipping rollback point."; exit 0; }
cd ~/rider-pi-api
if [ ! -d .git ]; then
  git init
  git config user.email "deploy@rider-pi.local"
  git config user.name "rider-pi deploy"
fi
git add -A
if git diff --staged --quiet; then
  echo "No changes – no new commit."
  exit 0
fi
MSG="deploy $(date -Iseconds)"
git commit -m "$MSG"
TAG="deploy-$(date +%Y%m%d-%H%M%S)"
git tag "$TAG"
echo "Rollback point: $TAG (Commit: $MSG)"
