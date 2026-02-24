#!/usr/bin/env python3
"""
server.py – MCP server for Rider-Pi. Control via any MCP-capable environment (Cursor, Claude Desktop, etc.).
Configuration via environment variables only (RIDER_PI_BASE_URL etc.). No hardcoded IPs.

Created: 2026-02-18
Last updated: 2026-02-18
"""

import base64
import json
import logging
import os
import sys

# Add src to path so rider_pi_api is found (before any other project imports)
_this_dir = os.path.dirname(os.path.abspath(__file__))
_src = os.path.dirname(_this_dir)
if _src not in sys.path:
    sys.path.insert(0, _src)

# Optional: load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from mcp.server.fastmcp import FastMCP
from rider_pi_api.client import RiderPiAPIError, get_client

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "WARNING").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("rider_pi_mcp")

mcp = FastMCP(
    "rider-pi",
    json_response=True,
)

# Names for the 6 emotes (action_id 1–6); support English and legacy German
EMOTE_NAMES = {
    "wiggle": 1,
    "wackeln": 1,
    "up_down": 2,
    "up/down": 2,
    "auf_ab": 2,
    "auf und ab": 2,
    "fwd_back": 3,
    "fwd/back": 3,
    "vor_zurueck": 3,
    "fwd and back": 3,
    "figure_8": 4,
    "figure-8": 4,
    "achten": 4,
    "circle": 5,
    "kreis": 5,
    "dance": 6,
    "tanz": 6,
}


def _emote_name_to_id(name: str) -> int:
    n = (name or "").strip().lower()
    if n in EMOTE_NAMES:
        return EMOTE_NAMES[n]
    if n.isdigit() and 1 <= int(n) <= 6:
        return int(n)
    raise ValueError(
        f"Unknown emote name: '{name}'. "
        f"Allowed: Wiggle, Up/down, Fwd/back, Figure-8, Circle, Dance (or 1–6)."
    )


@mcp.tool()
async def rider_pi_get_status() -> str:
    """Get current Rider-Pi status: connection, battery, uptime, robot_available."""
    try:
        api = get_client()
        data = await api.health()
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e), "connected": False})
    except Exception as e:
        logger.exception("rider_pi_get_status failed")
        return json.dumps({"error": str(e), "connected": False})


@mcp.tool()
async def rider_pi_get_battery() -> str:
    """Return battery level (0–100), charging, robot_available."""
    try:
        api = get_client()
        data = await api.battery()
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_get_battery failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_ready(height_mm: int = 95, balance_enabled: bool = True) -> str:
    """Put the robot in ready stance (balance + height). Call once before move/rotate."""
    try:
        api = get_client()
        data = await api.ready(height_mm=height_mm, balance_enabled=balance_enabled)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_ready failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_move_forward(duration: float = 1.0, speed: float = 0.5) -> str:
    """Drive forward (duration in seconds, speed 0–1)."""
    try:
        api = get_client()
        data = await api.move(direction="forward", speed=speed, duration=duration)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_move_forward failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_move_backward(duration: float = 1.0, speed: float = 0.5) -> str:
    """Drive backward (duration in seconds, speed 0–1)."""
    try:
        api = get_client()
        data = await api.move(direction="backward", speed=speed, duration=duration)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_move_backward failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_rotate(angle: float = 90.0, speed: float = 0.5) -> str:
    """Rotate the robot by angle degrees (positive = left, negative = right)."""
    try:
        api = get_client()
        data = await api.rotate(angle=angle, speed=speed)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_rotate failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_stop() -> str:
    """Immediate stop: cancel drive and any running animation."""
    try:
        api = get_client()
        data = await api.stop()
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_stop failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_expression(
    name_or_id: str = "dance",
) -> str:
    """Start a body expression/emote. name_or_id: Wiggle, Up/down, Fwd/back, Figure-8, Circle, Dance – or number 1–6 (emotes) or 1–35 (extended expressions)."""
    try:
        api = get_client()
        s = (name_or_id or "dance").strip()
        if s.isdigit():
            id_val = int(s)
            if 1 <= id_val <= 6:
                data = await api.action(action_id=id_val)
            else:
                data = await api.expression(expression_id=id_val)
        else:
            id_val = _emote_name_to_id(s)
            data = await api.action(action_id=id_val)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (RiderPiAPIError, ValueError) as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_expression failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_led(r: int = 128, g: int = 128, b: int = 128) -> str:
    """Set the RGB LED (r, g, b each 0–255)."""
    try:
        api = get_client()
        data = await api.led(r=r, g=g, b=b)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_led failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_capture_image() -> str:
    """Take a photo with the Pi camera and return it as Base64 JPEG (data URL)."""
    try:
        api = get_client()
        raw = await api.camera_snapshot()
        b64 = base64.standard_b64encode(raw).decode("ascii")
        return json.dumps({
            "ok": True,
            "data_url": f"data:image/jpeg;base64,{b64}",
            "bytes": len(raw),
        }, indent=2)
    except RiderPiAPIError as e:
        return json.dumps({"ok": False, "error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_capture_image failed")
        return json.dumps({"ok": False, "error": str(e)})


@mcp.tool()
async def rider_pi_combos_list() -> str:
    """List all saved combos (id, name, description)."""
    try:
        api = get_client()
        data = await api.combos_list()
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_combos_list failed")
        return json.dumps({"error": str(e)})


@mcp.tool()
async def rider_pi_combo_execute(combo_id: str) -> str:
    """Execute a saved combo (movement sequence). combo_id from rider_pi_combos_list."""
    try:
        api = get_client()
        data = await api.combo_execute(combo_id=combo_id)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except RiderPiAPIError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        logger.exception("rider_pi_combo_execute failed")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run(transport="stdio")
