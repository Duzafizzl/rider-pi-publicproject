---
title: SSH_NAVIGATION.md
description: Quick reference: folder structure on the Rider Pi for SSH navigation.
created: 2026-02-17
updated: 2026-02-24
---

# Rider Pi – SSH navigation

After `ssh pi@riderpi.local` (use your Pi hostname/IP; password if prompted) and `cd rider-pi-api` you see the API structure. **Full layout** (image vs. project on the Pi): see `FOLDER_STRUCTURE.md`.

In `~/rider-pi-api` on the Pi:

| Folder/File       | Purpose |
|-------------------|--------|
| **app/**          | App code: routes, services, deps, main.py |
| **app/routes/**   | API routes (movement, sensors, display, camera, …) |
| **app/services/** | Camera, face, audio services |
| **config/**       | Config (.env.example, later .env) |
| **data/**         | Persistent data: combos.json, map.json, known_faces/ |
| **scripts/**      | start.sh, deploy_rider_pi.sh, rider-pi-api.service |
| **logs/**         | Log files (when file logging is enabled) |
| **docs/**         | This documentation |
| **rider_pi_server.py** | Entry point – run with `python3 rider_pi_server.py` |
| **rider_pi_control.py** | Hardware wrapper (XGO), only relevant on the Pi |
| **requirements.txt**   | Python dependencies |

## Colored prompt (recognize Pi session)

To see at a glance that you are on the Pi (not on your Mac), run once:

```bash
# From your PC (password prompt if not using keys):
ssh pi@YOUR_PI_HOST 'bash -s' < scripts/setup_pi_prompt.sh
```

Or after SSH on the Pi: `bash ~/rider-pi-api/scripts/setup_pi_prompt.sh`. Then `pi@raspberrypi:~$` appears in **yellow**.

## Quick commands

```bash
# Start server (from project root)
./scripts/start.sh

# Or directly
python3 rider_pi_server.py

# Logs (systemd)
sudo journalctl -u rider-pi-api -f

# View combos
cat data/combos.json
```

## API base

- Health: `curl http://localhost:5050/health`
- Execute tool: `curl -X POST http://localhost:5050/api/execute -H "Content-Type: application/json" -d '{"tool":"get_battery_level","arguments":{}}'`
