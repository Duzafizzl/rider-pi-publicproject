# File: resonance.py
# Description: POST /api/resonance – Geste + Expression + LED in einem Paket.
# Created: 2026-02-16
# Last updated: 2026-02-16

from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException

from app import deps

router = APIRouter()


def _require_robot(robot: Optional[Any] = Depends(deps.get_robot_optional)) -> Any:
    if robot is None:
        raise HTTPException(status_code=503, detail="Robot not available (stub mode).")
    return robot


@router.post("/resonance")
def resonance(
    robot: Any = Depends(_require_robot),
    body: Optional[dict] = Body(None),
    pitch: int = 0,
    yaw: int = 0,
    roll: int = 0,
    expression_id: int = 1,
    led_r: int = 128,
    led_g: int = 128,
    led_b: int = 128,
    duration: float = 1.0,
    gesture_name: Optional[str] = None,
    intensity: Optional[float] = None,
    easing: Optional[str] = None,
):
    """
    POST /api/resonance – Alles-in-einem: Motor (roll/pitch/yaw), Expression, LED.
    Body (JSON): pitch, yaw, roll, expression_id, led_r/led_g/led_b oder led: {r,g,b},
    duration, gesture_name, intensity, easing.
    """
    if body:
        pitch = int(body.get("pitch", pitch))
        yaw = int(body.get("yaw", yaw))
        roll = int(body.get("roll", roll))
        expression_id = int(body.get("expression_id", expression_id))
        led = body.get("led")
        if isinstance(led, dict):
            led_r = int(led.get("r", led_r))
            led_g = int(led.get("g", led_g))
            led_b = int(led.get("b", led_b))
        else:
            led_r = int(body.get("led_r", led_r))
            led_g = int(body.get("led_g", led_g))
            led_b = int(body.get("led_b", led_b))
        duration = float(body.get("duration", duration))
        gesture_name = body.get("gesture_name", gesture_name)
        intensity = body.get("intensity", intensity)
        easing = body.get("easing", easing)
    expression_id = max(1, min(35, int(expression_id)))
    roll = max(-17, min(17, int(roll)))
    led_r = max(0, min(255, int(led_r)))
    led_g = max(0, min(255, int(led_g)))
    led_b = max(0, min(255, int(led_b)))
    duration = max(0.1, min(10.0, float(duration)))
    try:
        robot.adjust_roll(roll)
        robot.set_expression(expression_id)
        robot.set_rgb(led_r, led_g, led_b)
        out = {
            "ok": True,
            "message": "OK",
            "executed": {"roll": roll, "expression_id": expression_id, "led": [led_r, led_g, led_b]},
        }
        if gesture_name is not None:
            out["gesture_name"] = gesture_name
        if intensity is not None:
            out["intensity"] = intensity
        if easing is not None:
            out["easing"] = easing
        return out
    except Exception as e:
        return {"ok": False, "message": str(e)}
