# File: movement.py
# Description: Bewegung (move, rotate, stop, height, roll, balance, actions).
# Created: 2026-02-16
# Last updated: 2026-02-17

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException

from app import deps

router = APIRouter()


def _require_robot(robot: Optional[Any] = Depends(deps.get_robot_optional)) -> Any:
    if robot is None:
        raise HTTPException(status_code=503, detail="Robot not available (stub mode).")
    return robot


@router.post("/move")
def move(
    direction: str = "forward",
    speed: float = 0.5,
    duration: float = 1.0,
    robot: Any = Depends(_require_robot),
):
    """POST /api/move - Forward or backward."""
    speed = max(0.0, min(1.0, float(speed)))
    duration = max(0.1, min(10.0, float(duration)))
    if direction == "backward":
        msg = robot.move_backward(duration=duration, speed=speed)
    else:
        msg = robot.move_forward(duration=duration, speed=speed)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/rotate")
def rotate(
    angle: float = 0.0,
    speed: float = 0.5,
    robot: Any = Depends(_require_robot),
):
    """POST /api/rotate – Rotate (degrees)."""
    angle = max(-180.0, min(180.0, float(angle)))
    speed = max(0.0, min(1.0, float(speed)))
    msg = robot.rotate(angle=angle, speed=speed)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/stop")
def stop(robot: Any = Depends(_require_robot)):
    """POST /api/stop – Immediate stop (drive + rider_action animation + audio interrupt)."""
    try:
        from app.services.audio_playback_service import stop_playback
        stop_playback()
    except Exception:
        pass
    msg_stop = robot.stop()
    msg_reset = robot.reset()  # rider_reset() stops dance/expression animation
    ok = msg_stop.startswith("OK") and msg_reset.startswith("OK")
    return {"ok": ok, "message": "OK" if ok else f"stop={msg_stop}, reset={msg_reset}"}


@router.post("/height")
def height(height_mm: int = 95, robot: Any = Depends(_require_robot)):
    """POST /api/height – Height 75–115 mm."""
    height_mm = max(75, min(115, int(height_mm)))
    msg = robot.adjust_height(height_mm)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/roll")
def roll(roll_deg: int = 0, robot: Any = Depends(_require_robot)):
    """POST /api/roll – Roll -17..17."""
    roll_deg = max(-17, min(17, int(roll_deg)))
    msg = robot.adjust_roll(roll_deg)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/balance")
def balance(enabled: bool = True, robot: Any = Depends(_require_robot)):
    """POST /api/balance – Balance mode on/off."""
    msg = robot.set_balance_mode(enabled=enabled)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/ready")
def ready(
    height_mm: int = 95,
    balance_enabled: bool = True,
    robot: Any = Depends(_require_robot),
):
    """POST /api/ready – Put in ready stance: balance on + set height. Call once before move/rotate."""
    msgs = []
    msg_b = robot.set_balance_mode(enabled=balance_enabled)
    msgs.append(f"balance={msg_b}")
    height_mm = max(75, min(115, int(height_mm)))
    msg_h = robot.adjust_height(height_mm)
    msgs.append(f"height={msg_h}")
    ok = msg_b.startswith("OK") and msg_h.startswith("OK")
    return {"ok": ok, "message": "OK" if ok else "; ".join(msgs), "height_mm": height_mm, "balance": balance_enabled}


@router.post("/reset")
def reset(robot: Any = Depends(_require_robot)):
    """POST /api/reset – rider_reset(): Standardpose, bricht laufende rider_action (Tanz) ab."""
    msg = robot.reset()
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/action")
def action(action_id: int = 1, robot: Any = Depends(_require_robot)):
    """POST /api/action – Execute action 1–6."""
    action_id = max(1, min(6, int(action_id)))
    msg = robot.execute_action(action_id)
    return {"ok": msg.startswith("OK"), "message": msg}
