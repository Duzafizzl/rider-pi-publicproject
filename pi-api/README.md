---
title: README.md
description: Rider-Pi API server (runs on the Raspberry Pi). FastAPI app that controls the XGO robot.
created: 2026-02-18
updated: 2026-02-24
---

# Rider-Pi API (pi-api)

This folder contains the **API server that runs on the Rider Pi** (Raspberry Pi). It exposes HTTP endpoints (health, move, rotate, camera, combos, etc.) that the **MCP server** (on your PC) calls to control the robot.

## Requirements

- Raspberry Pi with Yahboom Rider-Pi hardware (or compatible XGO robot).
- Python 3.8+
- XGO library (`xgolib`) – usually provided with the Yahboom image or install per [Yahboom docs](https://github.com/YahboomTechnology/Rider-Pi-Robot).

## Quick start on the Pi

From the **project root** (if you cloned the full repo): `cd pi-api`.  
If you only copied `pi-api/` to the Pi (e.g. as `~/rider-pi-api`), you are already in the right folder.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp config/.env.example config/.env   # optional
export HOST=0.0.0.0 PORT=5050
python3 rider_pi_server.py
# or: ./run.sh
```

The server listens on `0.0.0.0:5050`. From your PC, set `RIDER_PI_BASE_URL=http://<PI_IP>:5050` and run the MCP server. For **autostart on boot**, run `./scripts/setup_pm2_on_pi.sh` once (see [docs/PM2_AUTOSTART.md](docs/PM2_AUTOSTART.md)).

## Deployment

**How to copy this onto the Rider Pi and run it** (including SSH, rsync/scp, and optional systemd): see **[../docs/DEPLOY_RIDER_PI.md](../docs/DEPLOY_RIDER_PI.md)**.

## Structure

| Path | Description |
|------|-------------|
| `rider_pi_server.py` | Entry point: starts the FastAPI app (uvicorn). |
| `rider_pi_control.py` | Hardware abstraction for the XGO robot. |
| `app/` | FastAPI app: `main.py`, routes (movement, sensors, display, camera, combos, etc.), services. |
| `config/.env.example` | Example env (HOST, PORT, LOG_LEVEL). Copy to `config/.env`. |
| `data/` | combos.json, map.json – start empty; see [data/README.md](data/README.md). |
| `scripts/` | start.sh, deploy_rider_pi.sh, setup_pm2_on_pi.sh, rollback, rider-pi-api.service (systemd). |

## Endpoints (used by the MCP server)

- `GET /health` – status, battery, robot_available
- `POST /api/ready`, `/api/move`, `/api/rotate`, `/api/stop`, `/api/action`, `/api/expression`, `/api/led`
- `GET /api/sensors`, `/api/battery`, `/api/combos`
- `POST /api/combos`, `POST /api/combos/{id}/execute`
- `GET /api/camera/snapshot`, `/api/camera/stream`
- and more (display, resonance, audio stubs, etc.)

**Camera dashboard:** Open `http://<PI_IP>:5050/camera` in a browser for the built-in live stream page (MJPEG + snapshot).

See the main repo [README](../README.md) and [DEPLOY_RIDER_PI.md](../docs/DEPLOY_RIDER_PI.md) for the full flow (PC MCP server ↔ Pi API ↔ robot).
