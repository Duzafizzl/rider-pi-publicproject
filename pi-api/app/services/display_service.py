# File: display_service.py
# Description: LCD-Anzeige per xgoscreen.LCD_2inch (nur auf dem Pi). Zeigt Text oder schwarzes Bild.
# Created: 2026-02-18
# Last updated: 2026-02-18

"""
Zeigt etwas auf dem physischen LCD des Rider Pi.
Nutzt xgoscreen.LCD_2inch (wie die Yahboom-Demos) – nur auf dem Pi mit installiertem xgoscreen.
"""

import logging
import math
import threading
import time
from typing import Callable, List, Optional, Tuple

logger = logging.getLogger("rider_pi.display_service")

# LCD 2inch typisch 320x240 (width, height bei PIL)
LCD_WIDTH = 320
LCD_HEIGHT = 240


def _get_display():
    """Import and create LCD instance. None on error (e.g. not on Pi)."""
    try:
        import xgoscreen.LCD_2inch as LCD_2inch
        return LCD_2inch.LCD_2inch()
    except ImportError as e:
        logger.debug("xgoscreen not available (only on Pi): %s", e)
        return None


def show_text_on_lcd(
    text: str = "Rider Pi",
    background: str = "black",
    skip_clear: bool = False,
    center: bool = True,
) -> Tuple[bool, str]:
    """
    Zeigt Text auf dem LCD (320x240). center=True: Text zentriert (horizontal + vertikal).
    skip_clear=True: no display.clear() before ShowImage → no white flash.
    Returns: (ok, message)
    """
    display = _get_display()
    if display is None:
        return False, "xgoscreen not available (only on Pi)"

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False, "PIL (Pillow) not installed"

    try:
        img = Image.new("RGB", (LCD_WIDTH, LCD_HEIGHT), background)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except OSError:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 32)
            except OSError:
                font = ImageFont.load_default()
        if center:
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except AttributeError:
                try:
                    w, h = draw.textsize(text, font=font)
                except Exception:
                    w, h = 80, 36
            x = (LCD_WIDTH - w) // 2
            y = (LCD_HEIGHT - h) // 2
        else:
            x, y = 80, 100
        draw.text((x, y), text, fill="white", font=font)
        if not skip_clear:
            display.clear()
        display.ShowImage(img)
        return True, "OK"
    except Exception as e:
        logger.exception("LCD show_text fehlgeschlagen")
        return False, str(e)


def show_word_bounce(
    text: str = "go!",
    duration_seconds: float = 1.0,
    skip_clear: bool = True,
    stop_event: Optional[threading.Event] = None,
) -> Tuple[bool, str]:
    """
    Show one word for duration_seconds with up/down motion (bounce).
    ~12 FPS, y oscillates sinusoidally (center 100, amplitude 25 px).
    stop_event: wenn gesetzt, Animation vorzeitig beenden.
    """
    display = _get_display()
    if display is None:
        return False, "xgoscreen not available (only on Pi)"

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False, "PIL (Pillow) not installed"

    try:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except OSError:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 32)
            except OSError:
                font = ImageFont.load_default()

        fps = 12
        num_frames = max(2, int(duration_seconds * fps))
        frame_duration = duration_seconds / num_frames
        center_y = 100
        amplitude = 25
        x = 80

        for frame in range(num_frames):
            if stop_event is not None and stop_event.is_set():
                break
            # Full sine: up → down → up (one cycle per word)
            t = frame / max(1, num_frames - 1)
            y = int(center_y + amplitude * math.sin(2 * math.pi * t))
            img = Image.new("RGB", (LCD_WIDTH, LCD_HEIGHT), "black")
            draw = ImageDraw.Draw(img)
            draw.text((x, y), text, fill="white", font=font)
            if not skip_clear and frame == 0:
                display.clear()
            display.ShowImage(img)
            if frame < num_frames - 1:
                time.sleep(frame_duration)
        return True, "OK"
    except Exception as e:
        logger.exception("LCD show_word_bounce fehlgeschlagen")
        return False, str(e)


def clear_lcd(skip_clear: bool = False) -> Tuple[bool, str]:
    """LCD black (no clear = no white flash when skip_clear=True)."""
    display = _get_display()
    if display is None:
        return False, "xgoscreen not available"
    try:
        from PIL import Image
        img = Image.new("RGB", (LCD_WIDTH, LCD_HEIGHT), "black")
        if not skip_clear:
            display.clear()
        display.ShowImage(img)
        return True, "OK"
    except Exception as e:
        return False, str(e)


# Default sentence: run once, word by word
DEFAULT_WORDS_SENTENCE = "I'm in! This is my body! Ready to go! Let's go!"


def show_words_loop(
    sentence: str = DEFAULT_WORDS_SENTENCE,
    delay_seconds: float = 1.0,
    on_word: Optional[Callable[[str, int], None]] = None,
) -> Tuple[bool, str]:
    """
    Show a sentence word by word on the LCD, once. Text always centered.
    on_word(word, index): optionaler Callback pro Wort (Roboter auf/ab, bei „go!“ Tanz + LED).
    """
    words: List[str] = [w.strip() for w in sentence.split() if w.strip()]
    if not words:
        return False, "No words"

    ok, msg = clear_lcd(skip_clear=True)
    if not ok:
        return False, msg

    for i, word in enumerate(words):
        ok, msg = show_text_on_lcd(text=word, background="black", skip_clear=True, center=True)
        if not ok:
            return False, f"Wort {i + 1}/{len(words)}: {msg}"
        if on_word:
            try:
                on_word(word, i)
            except Exception as e:
                logger.warning("on_word callback failed: %s", e, extra={"word": word, "index": i})
        if i < len(words) - 1:
            time.sleep(max(0.3, delay_seconds))

    return True, f"OK: {len(words)} words shown"


# --- Endless loop (stream mode): repeat word by word until stop ---
_words_loop_stop = threading.Event()
_words_loop_thread: Optional[threading.Thread] = None


def _words_loop_forever(
    sentence: str,
    delay_seconds: float,
    on_word: Optional[Callable[[str, int], None]] = None,
) -> None:
    """Runs in background thread: sentence word by word, repeated. Text centered. on_word=callback (robot up/down, on go! dance+LED)."""
    logger.info("Words loop started", extra={"sentence_preview": sentence[:50], "delay": delay_seconds})
    while not _words_loop_stop.is_set():
        words: List[str] = [w.strip() for w in sentence.split() if w.strip()]
        if not words:
            break
        clear_lcd(skip_clear=True)
        for i, word in enumerate(words):
            if _words_loop_stop.is_set():
                break
            ok, _ = show_text_on_lcd(text=word, background="black", skip_clear=True, center=True)
            if not ok:
                logger.warning("Words loop word failed", extra={"word_index": i + 1, "word": word})
            if on_word:
                try:
                    on_word(word, i)
                except Exception as e:
                    logger.warning("Words loop on_word failed: %s", e, extra={"word": word})
            if i < len(words) - 1 and not _words_loop_stop.is_set():
                time.sleep(max(0.3, delay_seconds))
    logger.info("Words loop stopped", extra={})


def start_words_loop(
    sentence: str = DEFAULT_WORDS_SENTENCE,
    delay_seconds: float = 1.0,
    on_word: Optional[Callable[[str, int], None]] = None,
) -> Tuple[bool, str]:
    """
    Start endless loop in background (word by word, repeated). Text centered.
    on_word(word, index): Callback pro Wort (Roboter auf/ab, bei „go!“ Tanz + LED). Stopp per stop_words_loop().
    """
    global _words_loop_thread
    if _words_loop_thread is not None and _words_loop_thread.is_alive():
        return False, "Loop already running"
    _words_loop_stop.clear()
    delay = max(0.3, min(3.0, float(delay_seconds)))
    sent = sentence or DEFAULT_WORDS_SENTENCE
    _words_loop_thread = threading.Thread(
        target=_words_loop_forever,
        args=(sent, delay, on_word),
        daemon=True,
        name="display_words_loop",
    )
    _words_loop_thread.start()
    return True, "Loop gestartet (Stopp: POST /api/display/stop_words)"


def stop_words_loop() -> Tuple[bool, str]:
    """Stoppt den laufenden Wort-Loop."""
    _words_loop_stop.set()
    if _words_loop_thread is not None and _words_loop_thread.is_alive():
        return True, "Stopp gesendet"
    return True, "No loop active"
