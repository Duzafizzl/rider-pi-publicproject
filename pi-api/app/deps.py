# File: deps.py
# Description: Shared FastAPI dependencies (robot singleton) for Rider Pi API.
# Created: 2026-02-17
# Last updated: 2026-02-17

from typing import Any, Optional

_robot: Optional[Any] = None


def get_robot_optional() -> Optional[Any]:
    """Return the robot instance or None if no hardware available."""
    return _robot


def set_robot(robot: Optional[Any]) -> None:
    global _robot
    _robot = robot


def init_robot() -> Optional[Any]:
    """Initialize the XGO robot if possible. Otherwise None (stub mode)."""
    try:
        from rider_pi_control import Robot
        robot = Robot()
        set_robot(robot)
        return robot
    except Exception:
        set_robot(None)
        return None
