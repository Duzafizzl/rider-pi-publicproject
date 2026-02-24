---
title: GIT_ROLLBACK.md
description: Git on the Rider Pi (~/rider-pi-api) – rollback points on each deploy.
created: 2026-02-17
updated: 2026-02-24
---

# Git and rollback on the Rider Pi

In `~/rider-pi-api` on the Pi there is a **separate Git repo** (only on the Pi, not the one on your PC). It is used only to create a rollback point after each deploy.

## Deploy flow

1. `./scripts/deploy_rider_pi.sh` syncs the project to `~/rider-pi-api` on the Pi (rsync).
2. **After that**, `scripts/pi_git_commit.sh` runs on the Pi:
   - If no repo yet: `git init` + user set
   - `git add -A` → `git commit -m "deploy …"` → **tag** `deploy-YYYYMMDD-HHMMSS`
3. Each deploy = one new commit + tag on the Pi. Previous states remain available.

## List rollback points (from your PC)

```bash
ssh pi@riderpi.local "cd ~/rider-pi-api && git log --oneline -10 && echo '' && git tag -l 'deploy-*' | tail -10"
```

## Perform rollback

**From your PC (recommended):**

```bash
cd /path/to/rider-pi-public/pi-api
./scripts/rollback_rider_pi.sh pi@riderpi.local deploy-20260217-141500
# or to previous commit: ./scripts/rollback_rider_pi.sh pi@riderpi.local HEAD~1
```

**Or via SSH on the Pi:**

```bash
ssh pi@riderpi.local
cd ~/rider-pi-api
git log --oneline          # Pick commit/tag
git reset --hard deploy-20260217-141500   # or HEAD~1
```

Then restart the server if needed: `./scripts/start.sh` or `sudo systemctl restart rider-pi-api` or `pm2 restart rider-pi-api`.

## Notes

- The **.git** in your local project is **not** synced to the Pi (excluded in rsync). The repo on the Pi is standalone and only holds deploy history.
- `.venv`, `__pycache__`, `logs/*.log` are in .gitignore and are not committed.
