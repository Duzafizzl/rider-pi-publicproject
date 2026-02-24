# File: face_service.py
# Description: dlib Face Recognition, known_faces DB (Phase 4).
# Created: 2026-02-16
# Last updated: 2026-02-16

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KNOWN_FACES_DIR = os.path.join(_ROOT, "data", "known_faces")
FACES_DB_JSON = os.path.join(KNOWN_FACES_DIR, "faces_db.json")
TOLERANCE = 0.55


def _ensure_dir():
    os.makedirs(KNOWN_FACES_DIR, exist_ok=True)


def _load_db() -> dict:
    if not os.path.isfile(FACES_DB_JSON):
        return {"faces": {}}
    try:
        with open(FACES_DB_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"faces": {}}


def _save_db(data: dict) -> None:
    _ensure_dir()
    with open(FACES_DB_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def remember_face(name: str, image_bytes: bytes) -> Dict[str, Any]:
    """
    Berechnet Face-Encoding vom Bild, speichert unter name.
    Returns: {ok, message, name} oder {ok: False, error}.
    """
    _ensure_dir()
    try:
        import face_recognition
        import numpy as np
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        encodings = face_recognition.face_encodings(arr)
        if not encodings:
            return {"ok": False, "error": "No face detected in image."}
        enc = encodings[0]
        npy_path = os.path.join(KNOWN_FACES_DIR, f"{name}.npy")
        np.save(npy_path, enc)
        db = _load_db()
        if "faces" not in db:
            db["faces"] = {}
        db["faces"][name] = {
            "name": name,
            "encoding_path": f"{name}.npy",
            "last_seen": datetime.utcnow().isoformat() + "Z",
            "times_seen": db["faces"].get(name, {}).get("times_seen", 0) + 1,
        }
        _save_db(db)
        return {"ok": True, "message": f"Gesicht '{name}' gespeichert.", "name": name}
    except ImportError as e:
        logger.warning("face_recognition not available: %s", e)
        return {"ok": False, "error": "face_recognition library not installed."}
    except Exception as e:
        logger.warning("remember_face failed: %s", e)
        return {"ok": False, "error": str(e)}


def identify_faces(image_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Vergleicht Bild mit allen bekannten Gesichtern.
    Returns: [{name, confidence, bbox: [x,y,w,h]}, ...]
    """
    try:
        import face_recognition
        import numpy as np
        from PIL import Image
        import io
        db = _load_db()
        known = db.get("faces", {})
        if not known:
            return []
        encodings_list = []
        names_list = []
        for name, meta in known.items():
            npy_path = os.path.join(KNOWN_FACES_DIR, meta.get("encoding_path", f"{name}.npy"))
            if not os.path.isfile(npy_path):
                continue
            enc = np.load(npy_path)
            encodings_list.append(enc)
            names_list.append(name)
        if not encodings_list:
            return []
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        arr = np.array(img)
        face_locs = face_recognition.face_locations(arr)
        face_encs = face_recognition.face_encodings(arr, face_locs)
        results = []
        for (top, right, bottom, left), enc in zip(face_locs, face_encs):
            matches = face_recognition.compare_faces(encodings_list, enc, tolerance=TOLERANCE)
            distances = face_recognition.face_distance(encodings_list, enc)
            best = np.argmin(distances) if len(distances) else None
            if best is not None and matches[best]:
                confidence = 1.0 - float(distances[best])
                results.append({
                    "name": names_list[best],
                    "confidence": round(confidence, 2),
                    "bbox": [int(left), int(top), int(right - left), int(bottom - top)],
                })
            else:
                results.append({"name": "unknown", "confidence": 0.0, "bbox": [int(left), int(top), int(right - left), int(bottom - top)]})
        return results
    except ImportError as e:
        logger.warning("face_recognition not available: %s", e)
        return []
    except Exception as e:
        logger.warning("identify_faces failed: %s", e)
        return []


def list_known_faces() -> List[Dict[str, Any]]:
    """Liste aller bekannten Gesichter mit last_seen, times_seen."""
    db = _load_db()
    faces = db.get("faces", {})
    return [
        {"name": name, "last_seen": meta.get("last_seen"), "times_seen": meta.get("times_seen", 0)}
        for name, meta in faces.items()
    ]


def delete_face(name: str) -> Dict[str, Any]:
    """Gesicht aus DB und .npy entfernen."""
    db = _load_db()
    faces = db.get("faces", {})
    if name not in faces:
        return {"ok": False, "error": f"'{name}' not found."}
    del faces[name]
    db["faces"] = faces
    _save_db(db)
    npy_path = os.path.join(KNOWN_FACES_DIR, f"{name}.npy")
    if os.path.isfile(npy_path):
        try:
            os.remove(npy_path)
        except Exception:
            pass
    return {"ok": True, "message": f"'{name}' deleted."}
