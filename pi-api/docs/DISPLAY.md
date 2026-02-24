---
title: DISPLAY.md
description: How the Rider Pi LCD is driven – image demo (Remix) vs. API server.
created: 2026-02-17
updated: 2026-02-24
---

# Display on the Rider Pi – what drives it?

The **small LCD** on the robot can be driven by two sources (when both exist on the Pi):

---

## 1. Yahboom image: Remix / main.py (“Wifi unconnected”)

**What may happen at Pi boot (when Remix autostarts):**

- **start1.sh** (in Pi home): starts `sudo python3 remix.py`
- **remix.py** → starts **main.py** (en/cn) from `RaspberryPi-CM4-main/`
- The **demos** (e.g. GPT-UI) use **xgoscreen.LCD_2inch**: `display = LCD_2inch.LCD_2inch()`, `display.ShowImage(splash)`.
- When the demo shows “offline”, **draw_offline()** from **demos/gpt_utils.py** is called:
  - **Text:** `"Wifi unconnected"`
  - **Image:** `pics/offline.png`

**Summary:** The **“Wifi unconnected”** message does **not** come from this API server; it comes from the **Yahboom demo** (RaspberryPi-CM4-main, gpt_utils.draw_offline). The display is driven there via **xgoscreen.LCD_2inch** and PIL/ImageDraw.

---

## 2. API server: rider_action = movement/animation (not LCD)

This API uses **xgolib**: `set_expression(expression_id)` → `self.car.rider_action(expression_id)`.

- **rider_action(1–35)** on the XGO Rider Pi is usually a **movement animation** (e.g. “dance”), **not** a static LCD image.
- The **LCD** is driven by the **Yahboom demo** (Remix, xgoscreen); **not** by rider_action.
- **Start expression on boot is disabled** so the robot does not keep “dancing”. Stop: `POST /api/stop`.

**To trigger movements:** `POST /api/expression?expression_id=1` (1–35) → robot runs the corresponding action. To stop: `POST /api/stop`.

**LCD control from this API:**
- **POST /api/display/show?text=…** – Show **text** on the LCD (uses xgoscreen.LCD_2inch on the Pi). Only on the Pi with xgoscreen installed.
- **POST /api/display/clear** – Clear LCD to black.
- **POST /api/display/show_words** – Show a sentence **word by word**, **text centered** on the LCD. **?loop=1**: endless loop; **stop:** **POST /api/display/stop_words**.
- Script: `./scripts/run_display_show.sh [Text]`.

---

## 3. Boot sequence

| Step        | What happens |
|------------|--------------------------------|
| Boot       | Depending on image: autostart of **start1.sh** (Remix) and/or **PM2** (this API). |
| Remix runs | main.py/demos draw on the LCD (e.g. “Wifi unconnected” in draw_offline()). |
| API runs   | Server answers /health, /api/*; **display only changes when** e.g. `/api/expression` is called. |

If **only** the API starts via PM2 and **Remix** does not autostart, the LCD can still show the last content drawn by Remix (“Wifi unconnected”) until something else (e.g. rider_action/expression) overwrites it.

---

## 4. What you can do

- **Get rid of “Unconnected” (with this API):**  
  On API startup, set an **expression** (e.g. expression 1) so xgolib runs **rider_action** and the LCD switches.
- **Check Remix autostart:**  
  On the Pi: `ls -la /home/pi/.config/autostart/` or systemd/session autostart; see if `start1.sh` or Remix is listed.
- **Use only this API:**  
  Disable Remix autostart, start the API with PM2 and use a start expression (or call `POST /api/expression?expression_id=1` once after startup).

Exact location in Yahboom code: **RaspberryPi-CM4-main/demos/gpt_utils.py**, function **draw_offline()**.
