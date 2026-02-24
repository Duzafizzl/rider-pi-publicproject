# File: combos.py
# Description: Movement combos CRUD, execute (from data/combos.json).
# Created: 2026-02-16
# Last updated: 2026-02-17

import json
import os
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel

from app import deps

router = APIRouter()


class ComboCreate(BaseModel):
    name: str
    description: str = ""
    sequence: List[dict] = []
    expression_id: int = 1


# Project root = 2 levels above app/routes/
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMBOS_PATH = os.path.join(_ROOT, "data", "combos.json")


def _load_combos() -> dict:
    if not os.path.isfile(COMBOS_PATH):
        return {"combos": []}
    try:
        with open(COMBOS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return {"combos": data}
        if not isinstance(data, dict):
            return {"combos": []}
        if "combos" not in data:
            data["combos"] = []
        return data
    except Exception:
        return {"combos": []}


def _save_combos(data: dict) -> None:
    os.makedirs(os.path.dirname(COMBOS_PATH), exist_ok=True)
    with open(COMBOS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@router.get("/combos")
def list_combos():
    """GET /api/combos – List all movement combos."""
    data = _load_combos()
    return {"ok": True, "combos": data.get("combos", [])}


@router.post("/combos")
def create_combo(body: ComboCreate = Body(...)):
    """POST /api/combos – Neue Combo anlegen. Body: name, description?, sequence?, expression_id?."""
    name = body.name
    description = body.description or ""
    sequence = body.sequence or []
    expression_id = body.expression_id
    data = _load_combos()
    combos = data.get("combos", [])
    ids = [int(c["id"]) for c in combos if c.get("id") is not None]
    new_id = str((max(ids) + 1) if ids else 1)
    combos.append({
        "id": new_id,
        "name": name,
        "description": description or "",
        "sequence": sequence,
        "expression_id": expression_id,
    })
    data["combos"] = combos
    _save_combos(data)
    return {"ok": True, "id": new_id, "message": f"Combo '{name}' angelegt."}


@router.post("/combos/{combo_id}/execute")
def execute_combo(combo_id: str, robot: Optional[Any] = Depends(deps.get_robot_optional)):
    """POST /api/combos/{id}/execute – Execute combo (requires robot)."""
    if robot is None:
        raise HTTPException(status_code=503, detail="Robot not available.")
    data = _load_combos()
    combos = data.get("combos", [])
    combo = next((c for c in combos if str(c.get("id")) == str(combo_id)), None)
    if not combo:
        raise HTTPException(status_code=404, detail=f"Combo '{combo_id}' not found.")
    sequence = combo.get("sequence", [])
    try:
        robot.set_expression(int(combo.get("expression_id", 1)))
        for step in sequence:
            if "angle" in step or "yaw" in step:
                robot.rotate(angle=float(step.get("angle", step.get("yaw", 0))), speed=float(step.get("speed", 0.5)))
            elif "direction" in step:
                duration = float(step.get("duration", 0.5))
                speed = float(step.get("speed", 0.5))
                if step.get("direction") == "backward":
                    robot.move_backward(duration=duration, speed=speed)
                else:
                    robot.move_forward(duration=duration, speed=speed)
            elif "duration" in step and "speed" not in step:
                import time
                time.sleep(float(step["duration"]))
        return {"ok": True, "message": f"Combo '{combo.get('name', combo_id)}' executed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
