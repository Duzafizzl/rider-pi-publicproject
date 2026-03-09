#!/usr/bin/env python3
"""
depth/ – Optional module: Apple Depth Pro for Rider Pi (obstacle detection, runs on the Mac).

Created: 2026-03-09
Last updated: 2026-03-09
"""

from .depth_service import (
    estimate_depth_from_image_bytes,
    estimate_depth_from_pi,
    obstacle_warning,
    preload_depth_model,
)

__all__ = [
    "estimate_depth_from_image_bytes",
    "estimate_depth_from_pi",
    "obstacle_warning",
    "preload_depth_model",
]
