---
title: ROADMAP.md
description: Rider-Pi mapping and visual SLAM roadmap – ORB-SLAM3, prior maps, Depth Pro, journey stream, and next steps.
created: 2026-03-09
updated: 2026-03-09
---

# Rider-Pi Mapping & Visual SLAM Roadmap

This document captures how we want the Rider Pi to build and use maps for in-home navigation, and how we plan to get there (visual SLAM, prior maps from phone scans, and the role of Depth Pro).

---

## Current state

- **No ROS/ROS2** on the Rider Pi; stack is Python (MCP server on PC ↔ FastAPI pi-api on Pi ↔ XGO).
- **Camera:** Single RGB camera via OpenCV (`VideoCapture(0)`), 640×480, 15 FPS (see `pi-api/app/services/camera_service.py`).
- **Depth:** No depth sensor on the Pi. Apple Depth Pro runs on the **Mac** (Pi snapshot → Depth Pro → depth zones for obstacle avoidance). See `depth/` in this repo.

---

## Goal: better in-home orientation

We want the Rider Pi to:

- Know where it is and build a map of the environment using only the existing RGB camera (no extra depth hardware or LiDAR at first).
- Use that map for navigation and orientation (and optionally combine it with a pre-built prior map).

---

## Visual SLAM strategy: ORB-SLAM3 (monocular, ROS2)

**Chosen approach:** Run **ORB-SLAM3** in **monocular** mode on the Rider Pi via ROS2.

- **Why monocular:** We only have one RGB camera; no depth sensor on the Pi.
- **Why ORB-SLAM3:** Well-supported, works on Raspberry Pi 5, has ROS2 wrappers (e.g. [ros2_orb_slam3](https://github.com/Mechazo11/ros2_orb_slam3)), and reference setups exist (e.g. [raspberry_pi_visual_slam](https://github.com/ozandmrz/raspberry_pi_visual_slam)).
- **Outcome:** Continuous pose estimate + sparse map; later we can derive a 2D occupancy grid for navigation.

**Planned scope (ticket):**

- Install ROS2 (Humble or newer) on the Rider Pi.
- Integrate ORB-SLAM3 as a ROS2 node (monocular).
- Publish Pi camera images on a ROS2 topic (e.g. `/camera/image_raw`) via OpenCV + `cv_bridge`.
- ORB-SLAM3 subscribes to that topic and publishes pose (and map).
- Add a small bridge in the Rider stack to consume pose (e.g. for logging or navigation).

**Out of scope for now:** RGB-D hardware (RealSense, etc.), dense 3D meshes, NeRF-style reconstruction.

---

## Journey stream (planned)

**Goal:** Capture a small number of images **while the robot is driving** (no stops), and return them as a simulated “livestream” (discrete frames) of the journey.

**Planned behaviour:**

- The robot drives for a configurable duration (e.g. 3 s) in one direction (forward/backward).
- During the drive, the Pi takes **6 snapshots** at regular intervals (e.g. every 0.5 s).
- The 6 JPEGs are returned in one response (e.g. as Base64 in JSON), so the client gets a short “journey grid” of the ride.

**Implementation (from plan):**

- **Pi-API:** New endpoint `POST /api/camera/journey-stream` with query params: `duration_sec`, `num_frames` (default 6), `direction`, `speed`. Move runs in a background thread; the request handler takes snapshots at fixed intervals and returns `{ "ok", "frames": [base64, ...], "num_frames", "duration_sec" }`.
- **MCP:** New tool `rider_pi_journey_stream` calling that endpoint and returning the same JSON (so Cursor/IDE can use the 6 images).
- **Client:** `rider_pi_api.client` gets a method `journey_stream(...)` for the new endpoint.

**References:** Plan in `.cursor/plans/` (journey stream 6 frames).

---

## Role of Depth Pro

- **Depth Pro does not provide pose or a global map.** It only estimates depth per image (and we use it for left/center/right zones for obstacle avoidance). So we **cannot** build the map from Depth Pro alone.
- **We keep Depth Pro** for reactive obstacle avoidance (e.g. "center < 0.4 m → stop").
- **Optional later:** Use Depth Pro as an extra depth source and fuse it with ORB-SLAM3 poses to get a denser or more metric map (hybrid approach). That would be a follow-up, not the first step.

---

## Prior map from phone scan (at robot height)

To have a **pre-built map** of the apartment at the same height as the Rider Pi's camera:

- **Idea:** Scan the apartment with a phone (iPhone Pro Max with LiDAR) at **floor / robot height** (~30 cm). That matches what the robot sees (table legs, skirting boards, under furniture).
- **Use:** The scan is converted to a 2D occupancy grid (slice at robot height) and used as a **prior map** for localization or path planning. Optionally, we run ORB-SLAM3 in localization-only mode in this known map.
- **Workflow:**
  1. Scan with a LiDAR app at floor level; export 3D (PLY or OBJ, metric).
  2. On a computer: load the mesh/point cloud, slice at robot height (e.g. 0.25 m), project to 2D, rasterize to an occupancy grid (PNG + YAML or similar).
  3. Load this map in the Rider stack (visualization, path planning, or as reference for SLAM/localization).

**Recommended apps (iPhone Pro Max):**

- **Polycam** – Room Mode, LiDAR, export OBJ/PLY; good default for "scan apartment at floor level."
- **Dot3D** – Higher accuracy, direct PLY export, no cloud; use when we need the best metric consistency.
- **RoomScan LiDAR** – Best when we mainly want a 2D floor plan (and less the full 3D point cloud).

---

## How we want to proceed

1. **Phase 1 – Visual SLAM on the Pi**
   - Implement the ORB-SLAM3 + ROS2 ticket: ROS2 on Pi, camera → ROS2 topic, ORB-SLAM3 monocular node, pose publishing, and a small Rider-side pose consumer (e.g. script or service).
   - Validate with a 2–3 minute run and trajectory visualization (e.g. RViz or simple script).

2. **Phase 2 – Prior map (optional)**
   - Use a phone scan (Polycam or Dot3D) at robot height; export PLY/OBJ.
   - Add a small pipeline (e.g. Python + Open3D/trimesh) to convert scan → 2D occupancy grid.
   - Integrate that map into the Rider stack (display and/or navigation).

3. **Phase 3 – Follow-ups (optional)**
   - Derive a 2D navigation map from SLAM (e.g. from ORB-SLAM3 map or point cloud).
   - Add a depth sensor and move to RGB-D SLAM (e.g. RTAB-Map) for metric 3D.
   - Explore hybrid: ORB-SLAM3 pose + Depth Pro depth for a denser map.

---

## References

- [RTAB-Map (ROS wiki)](http://wiki.ros.org/rtabmap_ros)
- [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3)
- [ros2_orb_slam3](https://github.com/Mechazo11/ros2_orb_slam3)
- [raspberry_pi_visual_slam](https://github.com/ozandmrz/raspberry_pi_visual_slam) – reference for ORB-SLAM3 + ROS2 on Raspberry Pi 5
- Depth Pro / obstacle avoidance: `depth/README.md` in this repo
