# File: audio.py
# Description: Audio abspielen, Stream (ElevenLabs-Chunks), Play mit URL/Base64 + Queue + Volume, Cues (Ping).
# Created: 2026-02-16
# Last updated: 2026-02-18

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/audio/play")
async def audio_play(
    body: Optional[dict] = Body(None),
    audio_url: Optional[str] = None,
    audio_data: Optional[str] = None,
    volume: float = 1.0,
):
    """
    POST /api/audio/play – MP3 abspielen (Queue).
    Body (JSON): audio_url (URL zum MP3) ODER audio_data (Base64-String), optional volume (0.0–1.0).
    """
    try:
        from app.services.audio_playback_service import enqueue_play, start_background_worker
        try:
            loop = asyncio.get_running_loop()
            start_background_worker(loop)
        except RuntimeError:
            pass
        data = body or {}
        url = data.get("audio_url") or audio_url
        b64 = data.get("audio_data") or audio_data
        vol = float(data.get("volume", volume))
        ok, msg = await enqueue_play(audio_url=url, audio_data_base64=b64, volume=vol)
        if ok:
            return JSONResponse(status_code=200, content={"ok": True, "message": msg})
        return JSONResponse(status_code=400, content={"ok": False, "error": msg})
    except Exception as e:
        logger.warning("audio/play failed: %s", e, extra={"module": "audio"})
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)},
        )


@router.post("/audio/stream")
async def audio_stream(request: Request):
    """POST /api/audio/stream – Receive MP3 bytes and enqueue (no overlap)."""
    try:
        body = await request.body()
        if not body or len(body) == 0:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "empty body"},
            )
        import base64
        from app.services.audio_playback_service import enqueue_play, start_background_worker
        try:
            loop = asyncio.get_running_loop()
            start_background_worker(loop)
        except RuntimeError:
            pass
        b64 = base64.b64encode(body).decode("ascii")
        ok, msg = await enqueue_play(audio_data_base64=b64, volume=1.0)
        if ok:
            return JSONResponse(
                status_code=200,
                content={"ok": True, "bytes_received": len(body), "message": msg},
            )
        return JSONResponse(status_code=400, content={"ok": False, "error": msg})
    except Exception as e:
        logger.warning("audio_stream failed: %s", e, extra={"module": "audio"})
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)},
        )


@router.post("/audio/cue")
async def audio_cue(
    body: Optional[dict] = Body(None),
    cue: Optional[str] = None,
    volume: float = 0.7,
):
    """
    POST /api/audio/cue – Short ping sound (e.g. listening / captured).
    Body (JSON): cue (listening | captured), optional volume (0.0–1.0).
    listening = play when rider enters listen mode.
    captured = play after capture (confirmation that something was recorded).
    """
    try:
        from app.services.audio_playback_service import enqueue_cue, start_background_worker, SUPPORTED_CUES
        try:
            loop = asyncio.get_running_loop()
            start_background_worker(loop)
        except RuntimeError:
            pass
        data = body or {}
        name = (data.get("cue") or cue or "").strip().lower()
        vol = float(data.get("volume", volume))
        if not name:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "Missing cue. Use cue: 'listening' or 'captured'."},
            )
        if name not in SUPPORTED_CUES:
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": f"Unknown cue: {name}. Supported: {list(SUPPORTED_CUES)}."},
            )
        ok, msg = await enqueue_cue(name, volume=vol)
        if ok:
            return JSONResponse(status_code=200, content={"ok": True, "cue": name, "message": msg})
        return JSONResponse(status_code=500, content={"ok": False, "error": msg})
    except Exception as e:
        logger.warning("audio/cue failed: %s", e, extra={"module": "audio"})
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": str(e)},
        )


@router.post("/speak")
async def speak():
    """POST /api/speak – TTS auf dem Pi (Fallback)."""
    return JSONResponse(
        status_code=501,
        content={"ok": False, "message": "Speak not implemented yet. Use /api/execute with tool=speak."},
    )
