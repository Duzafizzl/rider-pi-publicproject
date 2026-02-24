---
title: MOVEMENT_API.md
description: Control the robot (Rider Pi) via API – directly against the Pi or via a proxy.
created: 2026-02-17
updated: 2026-02-24
---

# Controlling the robot via API

**Important:** If the robot is not in a standing/ready pose yet, put it in **ready stance** (balance + height) first; otherwise move/rotate may not respond.

## 0. Put robot in ready stance (once before moving)

```bash
# Enable balance + height 95 mm (walking stance)
curl -X POST "http://riderpi.local:5050/api/ready"
# Optional: different height (75–115 mm)
curl -X POST "http://riderpi.local:5050/api/ready?height_mm=100"
```

## 1. Directly against the Rider Pi (port 5050)

The Pi must be reachable (e.g. `http://riderpi.local:5050`).

```bash
# Forward (0.5 s, speed 0.5)
curl -X POST "http://riderpi.local:5050/api/move?direction=forward&speed=0.5&duration=0.5"

# Backward
curl -X POST "http://riderpi.local:5050/api/move?direction=backward&speed=0.3&duration=1.0"

# Rotate (90°)
curl -X POST "http://riderpi.local:5050/api/rotate?angle=90&speed=0.5"

# Stop
curl -X POST "http://riderpi.local:5050/api/stop"

# Demo action (1–6), e.g. 6 = happy_dance
curl -X POST "http://riderpi.local:5050/api/action?action_id=6"
```

## 2. Via proxy (e.g. localhost:5000)

If a proxy is running with `RIDER_PI_BASE_URL=http://riderpi.local:5050`:

```bash
# Forward
curl -X POST "http://localhost:5000/api/rider-pi/move?direction=forward&speed=0.5&duration=0.5"

# Rotate
curl -X POST "http://localhost:5000/api/rider-pi/rotate?angle=-45&speed=0.5"

# Stop
curl -X POST "http://localhost:5000/api/rider-pi/stop"

# Demo action (happy_dance = 6)
curl -X POST "http://localhost:5000/api/rider-pi/action?action_id=6"
```

## Demo actions (action_id)

| action_id | Description      |
|-----------|------------------|
| 1         | Happy wiggle     |
| 2         | Wiggle up/down   |
| 3         | Forward/back     |
| 4         | Figure-eight     |
| 5         | Circle           |
| 6         | Happy dance      |
