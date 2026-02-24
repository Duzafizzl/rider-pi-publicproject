# File: __init__.py
# Description: Rider-Pi API client for public MCP server (ENV config only).
# Created: 2026-02-18
# Last updated: 2026-02-18

from .client import get_client, RiderPiAPIError

__all__ = ["get_client", "RiderPiAPIError"]
