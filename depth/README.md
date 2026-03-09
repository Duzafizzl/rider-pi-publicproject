---
title: depth/README.md
description: Optional module – Apple Depth Pro for Rider Pi (obstacle detection on the Mac).
created: 2026-03-09
updated: 2026-03-09
---

# Depth Pro for Rider Pi (optional)

This module adds **Apple Depth Pro** (ml-depth-pro) for Rider-Pi obstacle detection to this repo. It runs on the **Mac** (or another machine with Metal/MPS), not on the Pi.

## Flow

1. **Pi:** Sends a camera image (snapshot) via the Rider-Pi API.
2. **Mac:** This module loads the image, runs Depth Pro (MPS/CPU), and returns a depth map in metres.
3. **Zones:** The image is split into three horizontal zones (left 0–30%, center 30–70%, right 70–100%). The minimum distance per zone is computed.
4. **Obstacle logic:** `obstacle_warning(zones)` returns rules (e.g. center &lt; 0.4 m → STOP, &lt; 0.8 m → slow, tight sides → steer away).

## Usage

- **Standalone (e.g. script):**  
  `from depth import estimate_depth_from_image_bytes, obstacle_warning`
- **With Rider-Pi client:**  
  `from depth import estimate_depth_from_pi, obstacle_warning`  
  Client must provide `async def camera_snapshot() -> bytes` (e.g. `rider_pi_api.client.get_client()`).
- **Pre-load at startup:**  
  `from depth import preload_depth_model` and call `preload_depth_model()` once (e.g. when starting the MCP server or Substrate).

## Dependencies (optional)

Only required if you use Depth:

- **Python:** 3.8+
- **torch** (PyTorch, with MPS support on Apple Silicon)
- **depth_pro** (Apple [ml-depth-pro](https://github.com/apple/ml-depth-pro))

Example install:

```bash
pip install torch depth_pro
```

Without these packages, `preload_depth_model` and `estimate_depth_from_image_bytes` fail gracefully (log warning, return `None`).

## Where else it appears

- **miu-substrate:** The same logic runs in `services/depth_service.py`; the consciousness loop calls a depth check before movements. You can use this repo module as the single source and wire it into Substrate via import or copy.
- **Plan:** Phase 5 in the Rider-Pi masterplan (`.cursor/plans/`) describes the Depth Pro integration.

## API (overview)

| Function | Description |
|----------|-------------|
| `preload_depth_model()` | Load the model once (thread-safe). |
| `estimate_depth_from_image_bytes(image_bytes)` | Depth from JPEG bytes; returns zones + min_distance + inference_ms or None. |
| `estimate_depth_from_pi(client)` | Async: fetch snapshot from Pi and estimate depth. |
| `obstacle_warning(zones)` | From a zones dict, produce a warning (e.g. STOP / slow / steer away) or None. |
