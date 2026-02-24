# File: camera.py
# Description: MJPEG stream, snapshot, save photo.
# Created: 2026-02-16
# Last updated: 2026-02-16

import logging

from typing import Optional

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse, Response, StreamingResponse

from app.services import camera_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _mjpeg_stream():
    """Generator for MJPEG: boundary + chunk per frame."""
    for jpeg in camera_service.stream_frames():
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")


@router.get("/camera/stream")
async def camera_stream():
    """GET /api/camera/stream – MJPEG Stream (multipart/x-mixed-replace)."""
    return StreamingResponse(
        _mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"},
    )


@router.get("/camera/snapshot")
async def camera_snapshot():
    """GET /api/camera/snapshot – Einzelnes JPEG."""
    jpeg = camera_service.get_snapshot()
    if jpeg is None:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "message": "Camera not available."},
        )
    return Response(content=jpeg, media_type="image/jpeg")


@router.post("/camera/photo")
async def camera_photo(metadata: Optional[dict] = Body(None)):
    """POST /api/camera/photo – Foto speichern, optional Metadaten (timestamp, location)."""
    path = camera_service.save_photo(metadata=metadata or {})
    if path is None:
        return JSONResponse(
            status_code=503,
            content={"ok": False, "message": "Photo could not be saved."},
        )
    return {"ok": True, "path": path, "message": "Foto gespeichert."}
