---
title: FOLDER_STRUCTURE.md
description: File layout on the Rider Pi – image contents vs. API project.
created: 2026-02-17
updated: 2026-02-24
---

# Folder structure on the Rider Pi

After the first deploy, `/home/pi/` looks roughly like this. Two areas: **existing image** (touch only if needed) and **this project** (API server).

## Overview /home/pi/

```
/home/pi/
├── rider-pi-api/                 ← This project (API server). We work here.
│   ├── app/
│   ├── config/
│   ├── data/
│   ├── scripts/
│   ├── docs/
│   ├── logs/
│   ├── rider_pi_server.py
│   ├── rider_pi_control.py       (extended version)
│   ├── requirements.txt
│   └── run.sh
│
├── rider_pi_control.py            ← Original from image (leave unchanged)
├── start1.sh                     ← starts RaspberryPi-CM4-main/remix.py
├── Version.txt                   ← SD version info
├── Rider-pi_class/               ← Yahboom courses (notebooks, examples)
├── RaspberryPi-CM4-main/         ← Remix/demo (used by start1.sh)
├── xgoMusic/, xgoPictures/, xgoVideos/
├── model/
└── … (Desktop, Documents, .bashrc, etc.)
```

**Rule:** Everything for this API lives under e.g. `~/rider-pi-api/`. The rest belongs to the image or Yahboom courses – do not overwrite.

## Contents of ~/rider-pi-api/ (after deploy)

```
rider-pi-api/
├── rider_pi_server.py     # Entry: python3 rider_pi_server.py
├── rider_pi_control.py    # XGO hardware (extended version)
├── requirements.txt
├── run.sh                 # → scripts/start.sh
├── app/
│   ├── main.py
│   ├── deps.py
│   ├── routes/
│   └── services/
├── config/                 # .env here or in project root
├── data/                   # combos.json, map.json, known_faces/
├── scripts/                # start.sh, deploy_rider_pi.sh, rollback_rider_pi.sh, rider-pi-api.service, setup_pi_prompt
├── docs/
└── logs/
```

**SSH:** `cd ~/rider-pi-api` → then `./scripts/start.sh` or `python3 rider_pi_server.py`.

**systemd:** Service uses `WorkingDirectory=/home/pi/rider-pi-api`, starts `rider_pi_server.py`.

## Why this layout?

- **One folder, one purpose:** `rider-pi-api` = only this API code and its config/data. No mix with Rider-pi_class or Remix.
- **Image unchanged:** `rider_pi_control.py` in home, `Rider-pi_class`, `start1.sh` stay as from the image; we do not overwrite them.
- **Deploy:** Rsync only deploys to e.g. `~/rider-pi-api/`.
