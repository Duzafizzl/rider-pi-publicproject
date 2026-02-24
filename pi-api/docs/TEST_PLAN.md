---
title: TEST_PLAN.md
description: Test plan for all Rider Pi API tools and features – manual verification.
created: 2026-02-17
updated: 2026-02-24
---

# Rider Pi test plan – tools and features

Before checking off: **Rider Pi reachable** (e.g. `curl -s http://riderpi.local:5050/health` → `"status":"ok"`). Base URL for all examples: `BASE=http://riderpi.local:5050` (or proxy `http://localhost:5555` with `RIDER_PI_BASE_URL` set).

---

## 1. Base and health

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 1.1 | GET /health | `curl -s $BASE/health` | `status: ok`, `robot_available: true`, `battery` 0–100, `battery_raw` | ☐ |
| 1.2 | GET /api/execute (stub) | `curl -s -X POST $BASE/api/execute -H "Content-Type: application/json" -d '{"tool":"get_battery_level","arguments":{}}'` | `ok: true` or 503 if robot missing | ☐ |

---

## 2. Sensors

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 2.1 | GET /api/sensors | `curl -s $BASE/api/sensors` | `battery`, `battery_raw`, `attitude` (roll, pitch, yaw), `robot_available: true` | ☐ |
| 2.2 | GET /api/battery | `curl -s $BASE/api/battery` | `level` 0–100, `charging`, `robot_available` | ☐ |

---

## 3. Ready stance (before movement tests)

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 3.1 | POST /api/ready | `curl -s -X POST "$BASE/api/ready"` | `ok: true`, robot goes to stand/walk stance | ☐ |
| 3.2 | POST /api/balance | `curl -s -X POST "$BASE/api/balance?enabled=true"` | `ok: true` | ☐ |
| 3.3 | POST /api/height | `curl -s -X POST "$BASE/api/height?height_mm=95"` | `ok: true`, height visibly changed | ☐ |
| 3.4 | POST /api/roll | `curl -s -X POST "$BASE/api/roll?roll_deg=0"` | `ok: true` | ☐ |

---

## 4. Movement

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 4.1 | POST /api/move (forward) | After /api/ready: `curl -s -X POST "$BASE/api/move?direction=forward&speed=0.4&duration=0.5"` | `ok: true`, robot moves forward briefly | ☐ |
| 4.2 | POST /api/move (backward) | `curl -s -X POST "$BASE/api/move?direction=backward&speed=0.3&duration=0.5"` | `ok: true`, moves backward | ☐ |
| 4.3 | POST /api/rotate | `curl -s -X POST "$BASE/api/rotate?angle=45&speed=0.5"` | `ok: true`, rotates | ☐ |
| 4.4 | POST /api/stop | During/after movement: `curl -s -X POST "$BASE/api/stop"` | `ok: true`, stops immediately | ☐ |
| 4.5 | POST /api/action | `curl -s -X POST "$BASE/api/action?action_id=6"` (6 = Happy Dance) | `ok: true`, demo action runs (1–6) | ☐ |

---

## 5. Display (LCD + LED)

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 5.1 | POST /api/expression | `curl -s -X POST "$BASE/api/expression?expression_id=1"` | `ok: true`, LCD shows expression 1–35 | ☐ |
| 5.2 | POST /api/led | `curl -s -X POST "$BASE/api/led?r=0&g=255&b=0"` | `ok: true`, LED colored (e.g. green) | ☐ |

---

## 6. Resonance (gesture + expression + LED in one)

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 6.1 | POST /api/resonance | `curl -s -X POST "$BASE/api/resonance" -H "Content-Type: application/json" -d '{"pitch":5,"yaw":0,"roll":0,"expression_id":1,"led_r":128,"led_g":128,"led_b":255,"duration":1.0}'` | `ok: true` or 503 if robot missing; robot responds with pose + display + LED | ☐ |

---

## 7. Camera

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 7.1 | GET /api/camera/snapshot | `curl -s "$BASE/api/camera/snapshot" -o /tmp/snap.jpg && file /tmp/snap.jpg` | JPEG image or 503 if camera unavailable | ☐ |
| 7.2 | GET /api/camera/stream | In browser or VLC: `$BASE/api/camera/stream` | MJPEG stream runs (or 503) | ☐ |
| 7.3 | POST /api/camera/photo | `curl -s -X POST "$BASE/api/camera/photo" -H "Content-Type: application/json" -d '{}'` | `ok: true`, `path` set or 503 | ☐ |

---

## 8. Audio

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 8.1 | API structure | Routes: POST /api/audio/play, /api/audio/stream, /api/speak | Check docs/OpenAPI | ☐ |
| 8.2 | POST /api/audio/play | Optional: upload short MP3 (multipart) | 200 or 503, possibly sound from robot | ☐ |
| 8.3 | POST /api/speak | `curl -s -X POST "$BASE/api/speak" -H "Content-Type: application/json" -d '{"text":"Hello","language":"en"}'` | 200 or 503/501 (TTS may not be implemented) | ☐ |

---

## 9. Faces

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 9.1 | GET /api/faces/known | `curl -s "$BASE/api/faces/known"` | `ok: true`, `faces: []` or list of names | ☐ |
| 9.2 | POST /api/faces/remember | With image/body (name): e.g. current camera image + name | 200 or 503; face in known | ☐ |
| 9.3 | GET /api/faces/identify | `curl -s "$BASE/api/faces/identify"` | List with name, confidence, bbox or empty | ☐ |

---

## 10. Combos

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 10.1 | GET /api/combos | `curl -s "$BASE/api/combos"` | `ok: true`, `combos: []` or array | ☐ |
| 10.2 | POST /api/combos | Create new combo (name, description, sequence) | 200, combo in list | ☐ |
| 10.3 | POST /api/combos/{id}/execute | After create: execute with combo_id | `ok: true` or 404 | ☐ |

---

## 11. WebSocket

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 11.1 | WS /ws | With wscat or script: connect to `ws://riderpi.local:5050/ws`, send `{"type":"ping"}` | Receive `{"type":"pong","ts":...}` | ☐ |

---

## 12. Proxy (when proxy is running)

| # | Feature | Test step | Expected | ✓ |
|---|---------|-----------|----------|---|
| 12.1 | GET /api/rider-pi/status | `curl -s http://localhost:5555/api/rider-pi/status` | `connected: true`, battery, uptime | ☐ |
| 12.2 | POST /api/rider-pi/ready | `curl -s -X POST "http://localhost:5555/api/rider-pi/ready"` | Same as Pi /api/ready | ☐ |
| 12.3 | POST /api/rider-pi/move | `curl -s -X POST "http://localhost:5555/api/rider-pi/move?direction=forward&speed=0.4&duration=0.5"` | `ok: true` | ☐ |
| 12.4 | POST /api/rider-pi/rotate, /stop, /action | Same as direct Pi, via port 5555 | Same as direct | ☐ |

---

## 13. Acceptance checklist (summary)

- [ ] **Base:** Health, sensors, battery readable
- [ ] **Ready stance:** ready, balance, height – robot stands ready
- [ ] **Movement:** move (fwd/back), rotate, stop, action (1–6) – visible response
- [ ] **Display:** expression (1–35), LED (RGB) – visible
- [ ] **Resonance:** One call with pitch/yaw/roll + expression + LED – robot responds
- [ ] **Camera:** Snapshot returns image or 503
- [ ] **Faces:** known returns list; remember/identify optional
- [ ] **Combos:** list, create, execute – at least list OK
- [ ] **WebSocket:** /ws ping/pong
- [ ] **Proxy:** Status and at least move/ready via proxy

---

## Quick test (one line per category)

```bash
BASE=http://riderpi.local:5050
curl -s $BASE/health | jq .status
curl -s $BASE/api/sensors | jq .battery,.attitude
curl -s -X POST $BASE/api/ready
curl -s -X POST "$BASE/api/move?direction=forward&speed=0.3&duration=0.5"
curl -s -X POST $BASE/api/expression?expression_id=1
curl -s -X POST $BASE/api/led?r=255&g=0&b=0
curl -s $BASE/api/camera/snapshot -o /tmp/snap.jpg && file /tmp/snap.jpg
curl -s $BASE/api/faces/known
curl -s $BASE/api/combos
```

When done: check all ☐ and note the date.
