# File: client.py
# Description: Async HTTP client for Rider-Pi API. ENV config only, no hardcoded IPs.
# Created: 2026-02-18
# Last updated: 2026-02-18

import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# No default with real IP – user must set RIDER_PI_BASE_URL.
def _base_url() -> str:
    url = (os.getenv("RIDER_PI_BASE_URL") or "").strip()
    if not url or "YOUR_RIDER_PI" in url:
        raise ValueError(
            "RIDER_PI_BASE_URL is not set or still the placeholder. "
            "Create a .env file (see .env.example) and set your Rider-Pi URL, e.g. http://riderpi.local:5050"
        )
    return url.rstrip("/")


def _timeout() -> float:
    return float(os.getenv("RIDER_PI_TIMEOUT", "10.0"))


def _api_prefix() -> str:
    return (os.getenv("RIDER_PI_API_PREFIX") or "/api").rstrip("/") or "/api"


class RiderPiAPIError(Exception):
    """Error calling the Rider-Pi API."""
    pass


class _RiderPiClient:
    """Async client for the Rider-Pi FastAPI API. Config from ENV only."""

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    def _path(self, suffix: str) -> str:
        return f"{_api_prefix()}{suffix}"

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            base = _base_url()
            self._client = httpx.AsyncClient(
                base_url=base,
                timeout=_timeout(),
                headers={"Accept": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def health(self) -> Dict[str, Any]:
        """GET /health – Status, Battery, Uptime."""
        try:
            c = await self._get_client()
            r = await c.get("/health")
            r.raise_for_status()
            return r.json()
        except httpx.HTTPError as e:
            logger.exception("Rider-Pi health failed")
            raise RiderPiAPIError(str(e)) from e

    async def sensors(self) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.get(self._path("/sensors"))
        r.raise_for_status()
        return r.json()

    async def battery(self) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.get(self._path("/battery"))
        r.raise_for_status()
        return r.json()

    async def ready(self, height_mm: int = 95, balance_enabled: bool = True) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(
            self._path("/ready"),
            params={"height_mm": height_mm, "balance_enabled": balance_enabled},
        )
        r.raise_for_status()
        return r.json()

    async def move(
        self,
        direction: str = "forward",
        speed: float = 0.5,
        duration: float = 1.0,
    ) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(
            self._path("/move"),
            params={"direction": direction, "speed": speed, "duration": duration},
        )
        r.raise_for_status()
        return r.json()

    async def rotate(self, angle: float = 0.0, speed: float = 0.5) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(self._path("/rotate"), params={"angle": angle, "speed": speed})
        r.raise_for_status()
        return r.json()

    async def stop(self) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(self._path("/stop"))
        r.raise_for_status()
        return r.json()

    async def action(self, action_id: int = 1) -> Dict[str, Any]:
        """The 6 emotes: 1=Wiggle, 2=Up/down, 3=Fwd/back, 4=Figure-8, 5=Circle, 6=Dance."""
        action_id = max(1, min(6, int(action_id)))
        c = await self._get_client()
        r = await c.post(self._path("/action"), params={"action_id": action_id})
        r.raise_for_status()
        return r.json()

    async def expression(self, expression_id: int = 1) -> Dict[str, Any]:
        """Extended expressions (1–35)."""
        c = await self._get_client()
        r = await c.post(self._path("/expression"), params={"expression_id": expression_id})
        r.raise_for_status()
        return r.json()

    async def led(self, r: int = 128, g: int = 128, b: int = 128) -> Dict[str, Any]:
        c = await self._get_client()
        rq = await c.post(self._path("/led"), params={"r": r, "g": g, "b": b})
        rq.raise_for_status()
        return rq.json()

    async def combos_list(self) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.get(self._path("/combos"))
        r.raise_for_status()
        return r.json()

    async def combo_create(
        self,
        name: str,
        description: str = "",
        sequence: Optional[List[Dict[str, Any]]] = None,
        expression_id: int = 1,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "name": name,
            "description": description or "",
            "sequence": sequence or [],
            "expression_id": expression_id,
        }
        c = await self._get_client()
        r = await c.post(self._path("/combos"), json=payload)
        r.raise_for_status()
        return r.json()

    async def combo_execute(self, combo_id: str) -> Dict[str, Any]:
        c = await self._get_client()
        r = await c.post(self._path(f"/combos/{combo_id}/execute"))
        r.raise_for_status()
        return r.json()

    async def camera_snapshot(self) -> bytes:
        c = await self._get_client()
        r = await c.get(self._path("/camera/snapshot"))
        r.raise_for_status()
        return r.content

    async def camera_stream_url(self) -> str:
        return f"{_base_url()}{self._path('/camera/stream')}"


_client_instance: Optional[_RiderPiClient] = None


def get_client() -> _RiderPiClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = _RiderPiClient()
    return _client_instance
