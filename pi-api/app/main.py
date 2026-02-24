# File: main.py
# Description: FastAPI app for Rider Pi API. Health, routes, /api/execute, WebSocket, auto-flashlight.
# Created: 2026-02-17
# Last updated: 2026-02-24

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app import deps
from app.routes import movement, sensors, display, resonance, camera, audio, faces, combos

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("rider_pi")
_start_time = time.time()


def _log(level: str, message: str, **kwargs: Any) -> None:
    getattr(logger, level.lower())(message, extra=kwargs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    deps.init_robot()
    robot = deps.get_robot_optional()
    if robot:
        _log("info", "Robot (XGO) initialized", component="main")
        # Note: set_expression(id) = rider_action(id) = often movement/animation (dance), not LCD image.
        # LCD "Wifi unconnected" comes from Yahboom Remix (xgoscreen). Start expression disabled.
    else:
        logger.warning("Robot not available. API running in stub mode.", extra={"component": "main"})
    try:
        from app.services.audio_playback_service import start_background_worker
        start_background_worker(asyncio.get_running_loop())
    except Exception as e:
        logger.debug("Audio worker not started: %s", e)
    # Kill Yahboom system processes that fight over LED control (run as root)
    import subprocess
    for proc_name in ["remix.py", "main.py", "app_TwoCar.py"]:
        try:
            subprocess.run(
                ["sudo", "pkill", "-f", proc_name],
                timeout=3, capture_output=True,
            )
        except Exception:
            pass
    _log("info", "Yahboom processes stopped (LED control taken over)", component="main")
    await asyncio.sleep(0.5)

    # Green LED = Rider Pi API is alive
    _led_task = None
    if robot:
        robot.set_rgb(0, 255, 0)
        _log("info", "LED green – Rider Pi API online", component="main")

    # Auto-flashlight: in darkness -> white LEDs, in light -> green LEDs
    BRIGHTNESS_THRESHOLD = 40  # Average pixel brightness below which "dark" (0-255)
    FLASHLIGHT_CHECK_INTERVAL = 10  # Seconds between checks
    _flashlight_on = False

    async def _auto_flashlight_loop():
        nonlocal _flashlight_on
        await asyncio.sleep(5)  # Brief wait for camera ready
        while True:
            try:
                from app.services import camera_service
                jpeg = camera_service.get_snapshot()
                if jpeg and robot:
                    import cv2
                    import numpy as np
                    arr = np.frombuffer(jpeg, dtype=np.uint8)
                    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        avg_brightness = float(np.mean(img))
                        if avg_brightness < BRIGHTNESS_THRESHOLD and not _flashlight_on:
                            robot.set_rgb(255, 255, 255)
                            _flashlight_on = True
                            _log("info", "Flashlight ON (brightness: %.0f < %d)", avg_brightness, BRIGHTNESS_THRESHOLD, component="flashlight")
                        elif avg_brightness >= BRIGHTNESS_THRESHOLD and _flashlight_on:
                            robot.set_rgb(0, 255, 0)
                            _flashlight_on = False
                            _log("info", "Flashlight OFF, LED green (brightness: %.0f >= %d)", avg_brightness, BRIGHTNESS_THRESHOLD, component="flashlight")
            except Exception as e:
                _log("debug", "Flashlight check failed: %s", str(e), component="flashlight")
            await asyncio.sleep(FLASHLIGHT_CHECK_INTERVAL)

    _led_task = asyncio.create_task(_auto_flashlight_loop())

    _log("info", "Rider Pi server started (auto-flashlight active)", component="main", port=os.getenv("PORT", "5050"))
    yield
    # Shutdown: stop flashlight and LED
    if _led_task:
        _led_task.cancel()
    if robot:
        try:
            robot.set_rgb(0, 0, 0)
        except Exception:
            pass
    _log("info", "Rider Pi server shutting down", component="main")


app = FastAPI(
    title="Rider Pi API",
    description="API server for XGO Rider Pi. MCP-callable via POST /api/execute.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movement.router, prefix="/api", tags=["movement"])
app.include_router(sensors.router, prefix="/api", tags=["sensors"])
app.include_router(display.router, prefix="/api", tags=["display"])
app.include_router(resonance.router, prefix="/api", tags=["resonance"])
app.include_router(camera.router, prefix="/api", tags=["camera"])
app.include_router(audio.router, prefix="/api", tags=["audio"])
app.include_router(faces.router, prefix="/api", tags=["faces"])
app.include_router(combos.router, prefix="/api", tags=["combos"])


@app.get("/camera", response_class=HTMLResponse)
async def camera_viewer():
    """Page to view the camera live stream (MJPEG). Open: http://<pi-ip>:5050/camera"""
    path = os.path.join(os.path.dirname(__file__), "static", "camera_viewer.html")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="camera_viewer.html not found")


# WebSocket connections for real-time updates (sensor_update, face_detected, resonance_executed)
_ws_connections: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time: sensor_update, face_detected, movement_complete, resonance_executed."""
    await websocket.accept()
    _ws_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "ts": time.time()})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _ws_connections:
            _ws_connections.remove(websocket)


async def _broadcast_ws(event: dict) -> None:
    """Broadcast event to all WebSocket clients."""
    dead = []
    for ws in _ws_connections:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in _ws_connections:
            _ws_connections.remove(ws)


@app.get("/health")
def health():
    """Heartbeat for capability manager and dashboard."""
    robot = deps.get_robot_optional()
    battery = -1
    battery_raw = None
    if robot:
        try:
            battery = robot.get_battery_level()
            battery_raw = getattr(robot, "get_battery_raw", lambda: None)()
        except Exception as e:
            _log("warning", "Battery read failed", error=str(e), component="health")
    return {
        "status": "ok",
        "version": "0.1.0",
        "service": "rider_pi",
        "uptime_seconds": round(time.time() - _start_time, 1),
        "robot_available": robot is not None,
        "battery": battery if battery >= 0 else None,
        "battery_raw": battery_raw,
    }


@app.post("/api/execute")
def api_execute(payload: dict):
    """
    MCP-ansprechbar: Tool-Call per HTTP.
    Body: { "tool": "move_forward", "arguments": { "duration": 1.0, "speed": 0.5 } }
    """
    tool = payload.get("tool") or payload.get("name")
    arguments = payload.get("arguments") or payload.get("params") or {}
    if not tool or not isinstance(tool, str):
        raise HTTPException(status_code=400, detail="Missing or invalid 'tool' or 'name'")
    robot = deps.get_robot_optional()
    if not robot:
        return {
            "ok": False,
            "error": "robot_unavailable",
            "message": "No robot connected. API running in stub mode.",
            "tool": tool,
        }
    try:
        _log("info", "Execute tool", tool=tool, arguments=arguments, component="api_execute")
        fn = getattr(robot, tool, None)
        if fn is None or not callable(fn):
            return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool}", "tool": tool}
        if isinstance(arguments, dict):
            result = fn(**arguments)
        else:
            result = fn(*arguments) if isinstance(arguments, (list, tuple)) else fn()
        return {"ok": True, "tool": tool, "result": result}
    except Exception as e:
        _log("error", "Execute tool failed", tool=tool, error=str(e), component="api_execute")
        return {"ok": False, "error": "execution_error", "message": str(e), "tool": tool}
