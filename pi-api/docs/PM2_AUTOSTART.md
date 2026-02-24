---
title: PM2_AUTOSTART.md
description: Run the API with PM2 on the Rider Pi – autostart on boot.
created: 2026-02-17
updated: 2026-02-24
---

# PM2 autostart for the Rider Pi API

So that the Rider Pi API server starts automatically when the Pi boots, **PM2** is used.

## Prerequisites

- **Node.js** on the Pi (for PM2). If not installed, the setup script installs it via `apt` (or install it manually).
- **Python venv** in `~/rider-pi-api/.venv` with dependencies installed (`python3 -m venv .venv`, `pip install -r requirements.txt`). PM2 uses this venv so the API has access to FastAPI, uvicorn, and xgolib.

## Setup (one-time)

**Option A – directly on the Pi:**
```bash
ssh pi@YOUR_PI_HOST
cd ~/rider-pi-api
chmod +x scripts/setup_pm2_on_pi.sh
./scripts/setup_pm2_on_pi.sh
```

**Option B – from your PC (after deploy):**
```bash
# After rsync/scp of pi-api to ~/rider-pi-api on the Pi:
ssh pi@YOUR_PI_HOST 'cd ~/rider-pi-api && chmod +x scripts/setup_pm2_on_pi.sh && ./scripts/setup_pm2_on_pi.sh'
```

The script:
- Checks/installs Node.js and PM2
- Stops the old systemd service `rider-pi-api` if present (to avoid double start)
- Starts the API with PM2 (`ecosystem.config.cjs`)
- Enables autostart (`pm2 save` + `pm2 startup`)

## Files

| File | Purpose |
|------|---------|
| `ecosystem.config.cjs` | PM2 app: name `rider-pi-api`, interpreter `.venv/bin/python` (create venv first), port 5050, logs under `logs/` |
| `scripts/setup_pm2_on_pi.sh` | One-time setup on the Pi (Node/PM2, start, autostart) |

## Useful commands (on the Pi)

```bash
pm2 status              # Status of all apps
pm2 logs rider-pi-api       # Live logs
pm2 restart rider-pi-api   # Restart
pm2 stop rider-pi-api      # Stop
pm2 delete rider-pi-api    # Remove from PM2 (autostart remains until pm2 save overwrites)
```

## Alternative: systemd

If you prefer not to use Node/PM2 on the Pi, use systemd instead:

```bash
sudo cp ~/rider-pi-api/scripts/rider-pi-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rider-pi-api
sudo systemctl start rider-pi-api
```

See comments in `scripts/rider-pi-api.service`.
