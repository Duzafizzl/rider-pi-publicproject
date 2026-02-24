---
title: README.md
description: Rider-Pi MCP Server – public version, configurable via ENV, no Letta.
created: 2026-02-18
updated: 2026-02-24
---

# Rider-Pi MCP Server (public version)

Control your **Yahboom Rider-Pi** (XGO robot on Raspberry Pi) from any **MCP-capable tool**: Cursor, Claude Desktop, or other clients. No hardcoded IPs – configuration is **environment variables only**.

## Quick start (end-to-end)

1. **On the Pi:** Copy `pi-api/` to your Rider Pi, install dependencies, and run the API (see [Deploying the API on the Rider Pi](#deploying-the-api-on-the-rider-pi)). For autostart on boot, use the included PM2 script: `./scripts/setup_pm2_on_pi.sh` (see [docs/DEPLOY_RIDER_PI.md](docs/DEPLOY_RIDER_PI.md)).
2. **On your PC:** Clone this repo, create a venv, install deps, copy `.env.example` to `.env` and set `RIDER_PI_BASE_URL=http://<YOUR_PI_IP>:5050`.
3. **Start the MCP server** (e.g. from Cursor MCP settings or run `python3 src/rider_pi_mcp/server.py`). Your IDE can then use the Rider-Pi tools.

## What’s in this repo

| Part | Where | Runs on |
|------|--------|---------|
| **MCP server** | `src/` | Your PC/Mac – talks to Cursor/Claude and to the Pi API |
| **Rider-Pi API (pi-api)** | `pi-api/` | The Raspberry Pi – FastAPI app that controls the XGO robot |
| **Deploy guide** | `docs/DEPLOY_RIDER_PI.md` | How to copy pi-api onto the Pi and run it |

To use everything end-to-end: **deploy the pi-api on your Rider Pi** (see [Deploying the API on the Rider Pi](#deploying-the-api-on-the-rider-pi) below), then run the MCP server on your computer and set `RIDER_PI_BASE_URL` to your Pi’s address.

## Prerequisites

- **Python 3.8+**
- **Rider-Pi with a running Rider Pi API** (FastAPI on the Pi, e.g. port 5050), **or** access to an HTTP URL that serves this API (e.g. via proxy).
- Network access from the machine running the MCP server to the Rider-Pi (same WLAN/LAN).

## Installation (on your PC, for the MCP server)

```bash
git clone https://github.com/Duzafizzl/rider-pi-publicproject.git
cd rider-pi-public

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Copy the example env file and set **your** Rider-Pi URL:

```bash
cp .env.example .env
# Edit .env: set RIDER_PI_BASE_URL to your Pi address
```

**Examples for `RIDER_PI_BASE_URL`:**

- `http://riderpi.local:5050` (mDNS if the Pi is named that way)
- `http://192.168.1.100:5050` (fixed IP on your local network)
- If you reach the Pi via a proxy: proxy base URL + optionally `RIDER_PI_API_PREFIX=/api/rider-pi`

**No** IPs or hostnames are hardcoded – each user sets their own URL in `.env`.

## Start (stdio for MCP clients)

The server uses **stdio** (standard input/output) so Cursor/Claude Desktop can run it as a subprocess:

```bash
python3 src/rider_pi_mcp/server.py
```

### Use with Cursor

Add an entry in MCP settings (e.g. `~/.cursor/mcp.json` or project MCP config):

```json
{
  "mcpServers": {
    "rider-pi": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/rider-pi-public/src/rider_pi_mcp/server.py"],
      "env": {
        "RIDER_PI_BASE_URL": "http://YOUR_PI_ADDRESS:5050",
        "RIDER_PI_TIMEOUT": "10.0"
      }
    }
  }
}
```

Or without `env`: use a `.env` file in the project directory (loaded via `python-dotenv`).

### Claude Desktop

Similarly: point the MCP server config to `python` and `src/rider_pi_mcp/server.py`, and set `RIDER_PI_BASE_URL` in `env`.

## Available tools (MCP)

| Tool | Description |
|------|-------------|
| `rider_pi_get_status` | Status, battery, uptime, robot_available |
| `rider_pi_get_battery` | Battery level (0–100), charging |
| `rider_pi_ready` | Put robot in ready stance (before drive/rotate) |
| `rider_pi_move_forward` | Drive forward (duration, speed) |
| `rider_pi_move_backward` | Drive backward |
| `rider_pi_rotate` | Rotate (angle in degrees, speed) |
| `rider_pi_stop` | Immediate stop (drive + animation) |
| `rider_pi_expression` | Emote/expression: Wiggle, Up/down, Fwd/back, Figure-8, Circle, Dance (or ID 1–6 or 1–35) |
| `rider_pi_led` | Set RGB LED (r, g, b 0–255) |
| `rider_pi_capture_image` | Photo from Pi camera (Base64 JPEG) |
| `rider_pi_combos_list` | List saved combos |
| `rider_pi_combo_execute` | Run a saved combo |

## Deploying the API on the Rider Pi

The MCP server on your PC talks to the **Rider-Pi API**, which must run on the Raspberry Pi. This repo includes that API in **`pi-api/`**.

**To get the robot working:**

1. Copy **`pi-api/`** onto your Rider Pi (e.g. `rsync` or `scp` – see [docs/DEPLOY_RIDER_PI.md](docs/DEPLOY_RIDER_PI.md) for exact commands).
2. On the Pi: `cd` into the copied folder (e.g. `~/rider-pi-api`), create a venv, run `pip install -r requirements.txt`, then start the server: `./run.sh` or `python3 rider_pi_server.py` (default: port 5050).
3. **(Optional)** For autostart on boot: run `./scripts/setup_pm2_on_pi.sh` once on the Pi (installs PM2 and configures autostart).
4. On your PC: set `RIDER_PI_BASE_URL=http://<PI_IP_OR_HOSTNAME>:5050` in `.env` and start the MCP server.

**Full step-by-step** (SSH, rsync, PM2, systemd alternative): **[docs/DEPLOY_RIDER_PI.md](docs/DEPLOY_RIDER_PI.md)**.  
**Pi-side overview:** **[pi-api/README.md](pi-api/README.md)**.

## Rider-Pi API (pi-api)

This MCP server talks to the **Rider-Pi API** in `pi-api/`, which runs on the Pi and exposes the endpoints (health, move, rotate, stop, action/expression, LED, camera, combos). The API is compatible with the [Rider-Pi specification](https://github.com/YahboomTechnology/Rider-Pi-Robot) (XGO + FastAPI). If you already have a running compatible API at another URL or behind a proxy, set `RIDER_PI_BASE_URL` accordingly.

### Camera live stream (built-in dashboard)

Once the API is running on the Pi, a **camera dashboard** with live MJPEG stream is included:

- **URL:** `http://<PI_IP_OR_HOSTNAME>:5050/camera`
- **Contents:** Live video feed, snapshot button, and basic status. No extra setup – served from `pi-api/app/static/camera_viewer.html`.

## License

MIT (see LICENSE).

## Thanks

- Yahboom Rider-Pi / XGO
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
