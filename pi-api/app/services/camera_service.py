# File: camera_service.py
# Description: OpenCV Capture, MJPEG-Stream, Snapshot (Phase 3).
# Created: 2026-02-16
# Last updated: 2026-02-16

import io
import logging
import os
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)

_capture: Optional["cv2.VideoCapture"] = None
_lock = threading.Lock()
_latest_frame: Optional[bytes] = None
_camera_open = False

# Plan: 640x480, ~15 FPS
CAMERA_WIDTH = int(os.getenv("RIDER_PI_CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("RIDER_PI_CAMERA_HEIGHT", "480"))
CAMERA_FPS = 15
JPEG_QUALITY = 85


def _get_capture():
    global _capture, _camera_open
    with _lock:
        if _capture is not None and _capture.isOpened():
            return _capture
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.warning("Camera: OpenCV VideoCapture(0) failed to open")
                return None
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
            _capture = cap
            _camera_open = True
            return _capture
        except Exception as e:
            logger.warning("Camera: init failed: %s", e)
            return None


def _frame_to_jpeg(frame) -> bytes:
    import cv2
    ok, enc = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if not ok:
        return b""
    return enc.tobytes()


def get_snapshot() -> Optional[bytes]:
    """Single JPEG from current frame. None if camera not available."""
    cap = _get_capture()
    if cap is None:
        return None
    with _lock:
        ret, frame = cap.read()
    if not ret or frame is None:
        return None
    return _frame_to_jpeg(frame)


def stream_frames():
    """Generator: yield JPEG frames for MJPEG stream (multipart/x-mixed-replace)."""
    cap = _get_capture()
    if cap is None:
        return
    import cv2
    while True:
        with _lock:
            ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.1)
            continue
        jpeg = _frame_to_jpeg(frame)
        if jpeg:
            yield jpeg
        time.sleep(1.0 / CAMERA_FPS)


def save_photo(metadata: Optional[dict] = None) -> Optional[str]:
    """Save current photo to data/photos/ with timestamp. Return relative path."""
    jpeg = get_snapshot()
    if not jpeg:
        return None
    try:
        import cv2
        from datetime import datetime
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        photos_dir = os.path.join(root, "data", "photos")
        os.makedirs(photos_dir, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        name = f"photo_{ts}.jpg"
        path = os.path.join(photos_dir, name)
        with open(path, "wb") as f:
            f.write(jpeg)
        if metadata:
            meta_path = path + ".json"
            import json
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        return f"data/photos/{name}"
    except Exception as e:
        logger.warning("Camera: save_photo failed: %s", e)
        return None


def close_camera():
    global _capture, _camera_open
    with _lock:
        if _capture is not None:
            try:
                _capture.release()
            except Exception:
                pass
            _capture = None
        _camera_open = False
