# File: sensors.py
# Description: Sensoren (battery, attitude/IMU).
# Created: 2026-02-16
# Last updated: 2026-02-17

from typing import Any, Optional

from fastapi import APIRouter, Depends

from app import deps

router = APIRouter()


@router.get("/sensors")
def sensors(robot: Optional[Any] = Depends(deps.get_robot_optional)):
    """GET /api/sensors – Battery + Attitude (roll, pitch, yaw). battery_raw = Rohwert von xgolib (Debug)."""
    if robot is None:
        return {"battery": None, "battery_raw": None, "attitude": {"roll": 0, "pitch": 0, "yaw": 0}, "robot_available": False}
    try:
        battery = robot.get_battery_level()
        raw = getattr(robot, "get_battery_raw", lambda: None)()
        attitude = robot.get_attitude()
        return {
            "battery": battery,
            "battery_raw": raw,
            "attitude": attitude,
            "robot_available": True,
        }
    except Exception as e:
        return {
            "battery": None,
            "battery_raw": None,
            "attitude": {"roll": 0, "pitch": 0, "yaw": 0},
            "robot_available": True,
            "error": str(e),
        }


@router.get("/battery")
def battery(robot: Optional[Any] = Depends(deps.get_robot_optional)):
    """GET /api/battery – Nur Batteriestand."""
    if robot is None:
        return {"level": None, "charging": False, "robot_available": False}
    try:
        level = robot.get_battery_level()
        return {"level": level, "charging": False, "robot_available": True}
    except Exception as e:
        return {"level": None, "charging": False, "robot_available": True, "error": str(e)}
