---
title: DEPLOY_RIDER_PI.md
description: How to deploy the Rider-Pi API (pi-api) onto the Raspberry Pi so the MCP server can control the robot.
created: 2026-02-18
updated: 2026-02-18
---

# Deploying the Rider-Pi API onto the Robot

This guide explains how to get the **pi-api** (the FastAPI server that runs on the Rider Pi) onto your Raspberry Pi so that the **MCP server** (on your PC) can control the robot over the network.

## Overview

- **On your PC / Mac:** You run the MCP server (`src/rider_pi_mcp/server.py`) and point it at the Pi’s URL (`RIDER_PI_BASE_URL`).
- **On the Rider Pi:** You run the **pi-api** (FastAPI). It talks to the XGO hardware and exposes HTTP endpoints (health, move, rotate, camera, etc.).

Both must be on the same network (or reachable). The Pi runs the API; your computer runs the MCP server and your MCP client (e.g. Cursor).

---

## Prerequisites on the Rider Pi

1. **Hardware**
   - Yahboom Rider-Pi (or compatible Raspberry Pi + XGO robot).
   - Recommended: official [Yahboom Rider-Pi](https://github.com/YahboomTechnology/Rider-Pi-Robot) image or a Raspberry Pi OS image with the XGO library and device support.

2. **Software on the Pi**
   - Python 3.8 or newer.
   - The **xgolib** (XGO) library. On Yahboom images it is often pre-installed. Otherwise install according to [Yahboom’s docs](https://github.com/YahboomTechnology/Rider-Pi-Robot).
   - Network: the Pi must be on the same LAN as your PC (Wi‑Fi or Ethernet). Note the Pi’s IP or hostname (e.g. `riderpi.local` or `192.168.1.100`).

3. **Access**
   - SSH access to the Pi (e.g. `ssh pi@riderpi.local` or `ssh pi@192.168.1.100`). If you use a different user, replace `pi` in the commands below.

---

## Option A: Copy files with SCP/RSYNC (from your computer)

From the **rider-pi-public** repo on your computer:

1. **Copy the whole repo (or only `pi-api/`) to the Pi**

   Replace `pi@riderpi.local` with your Pi’s user and host (IP or hostname).

   ```bash
   cd /path/to/rider-pi-public
   rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' \
     pi-api/ pi@riderpi.local:~/rider-pi-api/
   ```

   Or with **scp** (copies the whole folder):

   ```bash
   scp -r pi-api pi@riderpi.local:~/
   ```

   So on the Pi the API lives in `~/rider-pi-api/` (or `~/pi-api/` if you renamed it).

2. **SSH into the Pi and install dependencies**

   ```bash
   ssh pi@riderpi.local
   cd ~/rider-pi-api
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   If the Pi image uses a specific XGO package (e.g. `xgo-pythonlib`), install it as per Yahboom’s instructions. The code expects `from xgolib import XGO`.

3. **Configure environment (optional)**

   ```bash
   cp config/.env.example config/.env
   # Edit config/.env if you want: HOST=0.0.0.0, PORT=5050, LOG_LEVEL=INFO
   ```

   Or set `HOST` and `PORT` when starting (see below).

4. **Run the API**

   **One-off (foreground):**

   ```bash
   source .venv/bin/activate
   export HOST=0.0.0.0
   export PORT=5050
   python3 rider_pi_server.py
   ```

   Or use the included script:

   ```bash
   chmod +x run.sh scripts/start.sh
   ./run.sh
   ```

   You should see the server listening on `0.0.0.0:5050`. The green LED on the robot often indicates “API is running”.

5. **Test from your PC**

   From your computer (same network):

   ```bash
   curl http://riderpi.local:5050/health
   ```

   You should get JSON with `status`, `battery`, `robot_available`, etc. Then set `RIDER_PI_BASE_URL=http://riderpi.local:5050` (or the Pi’s IP) in your MCP config and start the MCP server.

---

## Option B: Clone the repo on the Pi (if the Pi has internet)

1. **SSH into the Pi**

   ```bash
   ssh pi@riderpi.local
   ```

2. **Clone the repo and use pi-api**

   ```bash
   git clone https://github.com/Duzafizzl/rider-pi-publicproject.git
   cd rider-pi-publicproject/pi-api
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure and run** (same as Option A, steps 3–5)

   ```bash
   cp config/.env.example config/.env
   # optional: edit config/.env
   export HOST=0.0.0.0 PORT=5050
   python3 rider_pi_server.py
   ```

---

## Run the API at startup (optional)

So the API starts automatically after a reboot.

### PM2 (recommended – script included)

The repo includes a setup script that installs **Node.js/PM2** on the Pi and starts the API on boot:

```bash
# On the Pi (after deploy, from the pi-api / rider-pi-api folder):
cd ~/rider-pi-api
chmod +x scripts/setup_pm2_on_pi.sh
./scripts/setup_pm2_on_pi.sh
```

The script installs Node.js and PM2 if needed, starts the app with `ecosystem.config.cjs`, and enables autostart (`pm2 save` + `pm2 startup`). Then: `pm2 status`, `pm2 logs rider-pi-api`, `pm2 restart rider-pi-api`.

Details: **[pi-api/docs/PM2_AUTOSTART.md](pi-api/docs/PM2_AUTOSTART.md)**.

### systemd (alternative)

1. Create a unit file (adjust paths and user):

   ```bash
   sudo nano /etc/systemd/system/rider-pi-api.service
   ```

   Content (example):

   ```ini
   [Unit]
   Description=Rider-Pi API
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/rider-pi-api
   Environment="HOST=0.0.0.0"
   Environment="PORT=5050"
   ExecStart=/home/pi/rider-pi-api/.venv/bin/python rider_pi_server.py
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable rider-pi-api
   sudo systemctl start rider-pi-api
   sudo systemctl status rider-pi-api
   ```

The repo’s `pi-api/scripts/` folder may also contain a `rider-pi-api.service` that you can copy and adapt.

---

## Firewall

If you cannot reach the Pi on port 5050 from your PC, check:

- The API is bound to `0.0.0.0` (not `127.0.0.1`). Use `HOST=0.0.0.0`.
- No firewall on the Pi is blocking port 5050 (e.g. `sudo ufw allow 5050` if you use ufw).

---

## Summary

| Step | Where | What |
|------|--------|------|
| 1 | PC | Copy `pi-api/` to Pi (scp/rsync) or clone repo on Pi |
| 2 | Pi | `cd pi-api`, `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt` |
| 3 | Pi | `cp config/.env.example config/.env` (optional), then `python3 rider_pi_server.py` (or `./run.sh`) |
| 4 | PC | Set `RIDER_PI_BASE_URL=http://<PI_IP_OR_HOSTNAME>:5050` and run the MCP server |

After that, the MCP server on your PC can control the robot via the Pi API.
