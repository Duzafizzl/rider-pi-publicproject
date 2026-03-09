#!/usr/bin/env python3
"""
depth_service.py – Apple Depth Pro for Rider Pi (depth estimation, runs on the Mac).

Pi snapshot → Depth Pro (MPS/Metal) → depth map in metres.
Zones: left (0–30%), center (30–70%), right (70–100%) for obstacle avoidance.
Pre-load at server start via preload_depth_model().

Created: 2026-03-09
Last updated: 2026-03-09
"""

import logging
import os
import tempfile
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

ZONE_LEFT_END = 0.30
ZONE_CENTER_END = 0.70

_depth_model = None
_device = None
_loading = False


def _select_device():
    """Use MPS (Apple Metal GPU) if available, else CPU."""
    try:
        import torch
        if torch.backends.mps.is_available():
            logger.info("Depth Pro: MPS (Metal GPU) available – using GPU")
            return torch.device("mps")
    except Exception:
        pass
    logger.info("Depth Pro: Fallback to CPU")
    try:
        import torch
        return torch.device("cpu")
    except Exception:
        return None


def preload_depth_model():
    """Pre-load the model (e.g. at server start). Thread-safe."""
    global _depth_model, _device, _loading
    if _depth_model is not None or _loading:
        return
    _loading = True
    t0 = time.time()
    logger.info("Depth Pro: Starting pre-load...")
    try:
        import torch
        import depth_pro

        _device = _select_device()
        precision = torch.float32
        model, transform = depth_pro.create_model_and_transforms(
            device=_device or torch.device("cpu"),
            precision=precision,
        )
        model.eval()
        _depth_model = (model, transform)
        elapsed = time.time() - t0
        logger.info("Depth Pro: Model loaded in %.1fs on %s", elapsed, _device)
    except ImportError as e:
        logger.warning("depth_pro not installed: %s", e)
    except Exception as e:
        logger.warning("Depth Pro pre-load failed: %s", e)
    finally:
        _loading = False


def _get_depth_model():
    """Lazy load Depth Pro (apple/ml-depth-pro) with MPS support."""
    global _depth_model, _device
    if _depth_model is not None:
        return _depth_model
    preload_depth_model()
    return _depth_model


def estimate_depth_from_image_bytes(image_bytes: bytes) -> Optional[Dict[str, Any]]:
    """
    Run Depth Pro on the image (e.g. from Pi snapshot).
    Returns: {
        "focallength_px": float,
        "zones": {"left": min_m, "center": min_m, "right": min_m},
        "min_distance": float (global minimum),
        "inference_ms": int,
    } or None if not available.
    """
    model_data = _get_depth_model()
    if model_data is None:
        return None
    model, transform = model_data
    try:
        import depth_pro
        import numpy as np
        t0 = time.time()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(image_bytes)
            path = f.name
        try:
            image, _, f_px = depth_pro.load_rgb(path)
            image = transform(image)
            prediction = model.infer(image, f_px=f_px)
            depth = prediction["depth"]
            if hasattr(depth, "cpu"):
                depth = depth.cpu()
            if hasattr(depth, "numpy"):
                depth = depth.numpy()
            depth = np.asarray(depth)
            if depth.ndim == 3:
                depth = depth.squeeze()
            left_end = int(depth.shape[1] * ZONE_LEFT_END)
            center_end = int(depth.shape[1] * ZONE_CENTER_END)
            left_zone = depth[:, :left_end]
            center_zone = depth[:, left_end:center_end]
            right_zone = depth[:, center_end:]

            def safe_min(arr):
                try:
                    return float(np.nanmin(arr[arr > 0])) if np.any(arr > 0) else None
                except Exception:
                    return None

            elapsed_ms = int((time.time() - t0) * 1000)
            logger.info(
                "Depth Pro inference: %dms  zones L=%.2f M=%.2f R=%.2f",
                elapsed_ms,
                safe_min(left_zone) or -1,
                safe_min(center_zone) or -1,
                safe_min(right_zone) or -1,
            )
            return {
                "focallength_px": float(prediction.get("focallength_px", 0)),
                "zones": {
                    "left": safe_min(left_zone),
                    "center": safe_min(center_zone),
                    "right": safe_min(right_zone),
                },
                "min_distance": safe_min(depth),
                "inference_ms": elapsed_ms,
            }
        finally:
            try:
                os.unlink(path)
            except Exception:
                pass
    except Exception as e:
        logger.warning("Depth Pro inference failed: %s", e)
        return None


async def estimate_depth_from_pi(client: Any) -> Optional[Dict[str, Any]]:
    """
    Fetch snapshot from Rider Pi and estimate depth (Mac).
    client: Object with async def camera_snapshot() -> bytes (e.g. rider_pi_api.client.get_client()).
    """
    try:
        jpeg = await client.camera_snapshot()
        return estimate_depth_from_image_bytes(jpeg)
    except Exception as e:
        logger.warning("estimate_depth_from_pi failed: %s", e)
        return None


def obstacle_warning(zones: Dict[str, Optional[float]]) -> Optional[str]:
    """
    Reactive rules: center < 0.4 m → STOP, center < 0.8 m → slow, sides → steer away.
    Returns: Warning message or None.
    """
    center = zones.get("center")
    left = zones.get("left")
    right = zones.get("right")
    if center is not None and center < 0.4:
        return "Obstacle directly ahead! Stopping."
    if center is not None and center < 0.8:
        return "Obstacle close ahead – drive slowly."
    if left is not None and left < 0.3:
        return "Left tight – steer right."
    if right is not None and right < 0.3:
        return "Right tight – steer left."
    return None
