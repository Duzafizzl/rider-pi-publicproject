# File: audio_playback_service.py
# Description: Audio queue and playback (MP3 from URL/Base64), interrupt on rider_stop, cues (ping).
# Created: 2026-02-18
# Last updated: 2026-02-18

"""
Audio Playback Service: Queue-based, one item after another.
On rider_stop current playback is interrupted.
Cues: Short ping sounds (listening, captured) – from static/sounds or generated beep.
"""

import asyncio
import base64
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("rider_pi.audio")

# Cue files: app/static/sounds/<name>.mp3 (optional). Fallback: ffmpeg beep.
_CUES_DIR = Path(__file__).resolve().parent.parent / "static" / "sounds"
SUPPORTED_CUES = ("listening", "captured")
# Frequencies for fallback beep (Hz), duration (seconds)
_CUE_BEEP_SPECS = {"listening": (880, 0.15), "captured": (660, 0.2)}

# Global reference to current play process (for interrupt)
_current_process: Optional[subprocess.Popen] = None
_play_queue: asyncio.Queue = asyncio.Queue()
_worker_started = False
_interrupt_requested = False


def _play_mp3_sync(path: str, volume: float = 1.0) -> None:
    """Sync: play MP3. volume 0.0–1.0 (applied as gain)."""
    global _current_process, _interrupt_requested
    path_clean = str(Path(path).resolve())
    if not os.path.isfile(path_clean):
        return
    # Gain: 0.0 -> -100 (mute), 1.0 -> 0 (normal). Rough formula: dB = (volume - 1) * 40
    gain_db = (float(volume) - 1.0) * 40.0 if 0 <= volume <= 1 else 0.0
    gain_db = max(-100, min(0, gain_db))
    try:
        mpg123 = shutil.which("mpg123")
        if mpg123:
            cmd = [mpg123, "-q", "--gain", str(int(gain_db)), path_clean]
            _current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _current_process.wait()
            _current_process = None
            return
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            vol_filter = f"volume={volume:.2f}" if 0 < volume <= 2 else "volume=1.0"
            cmd = [ffmpeg, "-y", "-i", path_clean, "-filter:a", vol_filter, "-f", "alsa", "-"]
            _current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _current_process.wait()
            _current_process = None
    except Exception as e:
        logger.warning("play_mp3_sync failed: %s", e, extra={"path": path_clean})
    finally:
        _current_process = None
        try:
            if os.path.isfile(path_clean):
                os.unlink(path_clean)
        except OSError:
            pass


def _generate_beep_mp3(frequency_hz: int, duration_sec: float) -> Optional[str]:
    """Create a short MP3 beep file with ffmpeg (lavfi sine). Return temp path or None."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    try:
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        # lavfi sine, 1 Kanal, 22.05 kHz, dann nach MP3
        cmd = [
            ffmpeg, "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"sine=frequency={frequency_hz}:duration={duration_sec}",
            "-ac", "1", "-ar", "22050", path,
        ]
        subprocess.run(cmd, capture_output=True, timeout=5, check=True)
        return path if os.path.isfile(path) else None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.debug("beep generation failed: %s", e, extra={"module": "audio_playback_service"})
        return None


def get_cue_play_path(cue_name: str) -> Optional[str]:
    """
    Return a playback path for the cue (temp file).
    Nutzt static/sounds/<cue_name>.mp3 falls vorhanden, sonst generierten Beep.
    """
    if cue_name not in SUPPORTED_CUES:
        return None
    local = _CUES_DIR / f"{cue_name}.mp3"
    if local.is_file():
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            shutil.copy2(local, path)
            return path
        except OSError:
            if os.path.isfile(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
            return None
    spec = _CUE_BEEP_SPECS.get(cue_name, (880, 0.15))
    return _generate_beep_mp3(spec[0], spec[1])


async def enqueue_play_file(path: str, volume: float = 1.0) -> tuple[bool, str]:
    """Enqueue a local file (path). path is deleted after playback."""
    if not path or not os.path.isfile(path):
        return False, "File not found"
    volume = max(0.0, min(1.0, float(volume)))
    _ensure_worker()
    await _play_queue.put((path, volume))
    return True, "Queued for playback"


async def enqueue_cue(cue_name: str, volume: float = 0.7) -> tuple[bool, str]:
    """
    Play a short audio cue (ping): listening = \"listening\", captured = \"capture confirmed\".
    Nutzt static/sounds/<cue_name>.mp3 oder Fallback-Beep.
    """
    path = get_cue_play_path(cue_name)
    if not path:
        return False, f"Unknown or unsupported cue: {cue_name}"
    return await enqueue_play_file(path, volume)


def stop_playback() -> None:
    """Sofortige Unterbrechung der aktuellen Wiedergabe (z. B. bei rider_stop)."""
    global _current_process, _interrupt_requested
    _interrupt_requested = True
    if _current_process and _current_process.poll() is None:
        try:
            _current_process.terminate()
            _current_process.wait(timeout=2)
        except Exception as e:
            logger.debug("stop_playback terminate: %s", e)
            try:
                _current_process.kill()
            except Exception:
                pass
        _current_process = None
    logger.info("Audio playback stopped (interrupt)", extra={"module": "audio_playback_service"})


_worker_task: Optional[asyncio.Task] = None


async def _worker() -> None:
    """Hintergrund-Worker: verarbeitet die Warteschlange nacheinander."""
    global _interrupt_requested
    loop = asyncio.get_event_loop()
    while True:
        try:
            item = await _play_queue.get()
            if item is None:
                break
            path, volume = item
            _interrupt_requested = False
            await loop.run_in_executor(None, _play_mp3_sync, path, volume)
            if _interrupt_requested:
                break
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("audio worker item failed: %s", e, extra={"module": "audio_playback_service"})


def start_background_worker(loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
    """Startet den Audio-Worker (aus lifespan aufrufen)."""
    global _worker_started, _worker_task
    if _worker_started:
        return
    try:
        loop = loop or asyncio.get_running_loop()
    except RuntimeError:
        return
    _worker_task = loop.create_task(_worker())
    _worker_started = True
    logger.info("Audio playback worker started", extra={"module": "audio_playback_service"})


def _ensure_worker() -> None:
    """Ensure the worker is running (called on first enqueue if not already started in lifespan)."""
    global _worker_started, _worker_task
    if _worker_started:
        return
    try:
        loop = asyncio.get_running_loop()
        _worker_task = loop.create_task(_worker())
        _worker_started = True
    except RuntimeError:
        pass


async def enqueue_play(
    audio_url: Optional[str] = None,
    audio_data_base64: Optional[str] = None,
    volume: float = 1.0,
) -> tuple[bool, str]:
    """
    MP3 in die Warteschlange legen: entweder audio_url (wird heruntergeladen) oder audio_data_base64.
    volume 0.0–1.0. Returns (ok, message).
    """
    import aiohttp
    volume = max(0.0, min(1.0, float(volume)))
    path = None
    try:
        if audio_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return False, f"Download failed: HTTP {resp.status}"
                    body = await resp.read()
        elif audio_data_base64:
            try:
                body = base64.b64decode(audio_data_base64)
            except Exception as e:
                return False, f"Invalid base64: {e}"
        else:
            return False, "Provide audio_url or audio_data (base64)"
        if not body or len(body) < 100:
            return False, "Empty or too small audio data"
        fd, path = tempfile.mkstemp(suffix=".mp3")
        try:
            os.write(fd, body)
            os.close(fd)
            fd = None
        except Exception:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
            if path and os.path.isfile(path):
                os.unlink(path)
            return False, "Write temp file failed"
        _ensure_worker()
        await _play_queue.put((path, volume))
        return True, "Queued for playback"
    except Exception as e:
        if path and os.path.isfile(path):
            try:
                os.unlink(path)
            except OSError:
                pass
        logger.warning("enqueue_play failed: %s", e, extra={"module": "audio_playback_service"})
        return False, str(e)
