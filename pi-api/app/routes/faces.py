# File: faces.py
# Description: Remember/identify faces (dlib).
# Created: 2026-02-16
# Last updated: 2026-02-16

from typing import Optional

from fastapi import APIRouter, Body, HTTPException

from app.services import camera_service, face_service

router = APIRouter()


@router.post("/faces/remember")
async def faces_remember(body: Optional[dict] = Body(None)):
    """POST /api/faces/remember – Aktuelles Kamerabild als Gesicht unter name speichern. Body: {name: \"Clary\"}."""
    name = (body or {}).get("name")
    if not name or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="Body muss { \"name\": \"...\" } enthalten.")
    snapshot = camera_service.get_snapshot()
    if not snapshot:
        raise HTTPException(status_code=503, detail="Camera not available.")
    result = face_service.remember_face(name.strip(), snapshot)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
    return result


@router.get("/faces/identify")
async def faces_identify():
    """GET /api/faces/identify – Wer ist gerade im Bild? [{name, confidence, bbox}]."""
    snapshot = camera_service.get_snapshot()
    if not snapshot:
        raise HTTPException(status_code=503, detail="Camera not available.")
    results = face_service.identify_faces(snapshot)
    return {"ok": True, "faces": results}


@router.get("/faces/known")
async def faces_known():
    """GET /api/faces/known – Liste aller bekannten Gesichter."""
    return {"ok": True, "faces": face_service.list_known_faces()}


@router.delete("/faces/{name}")
async def faces_delete(name: str):
    """DELETE /api/faces/{name} – Gesicht vergessen."""
    result = face_service.delete_face(name)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("error", "Nicht gefunden"))
    return result
