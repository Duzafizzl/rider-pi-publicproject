# File: display.py
# Description: Display (LCD-Text, Expression 1–35 = Bewegung, LED).
# Created: 2026-02-16
# Last updated: 2026-02-18

import logging
import threading
import time
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app import deps
from app.services import display_service

logger = logging.getLogger("rider_pi.display")

router = APIRouter()


def _require_robot(robot: Optional[Any] = Depends(deps.get_robot_optional)) -> Any:
    if robot is None:
        raise HTTPException(status_code=503, detail="Robot not available (stub mode).")
    return robot


@router.post("/expression")
def expression(
    expression_id: int = 1,
    robot: Any = Depends(_require_robot),
):
    """POST /api/expression – rider_action(1–35) = movement/animation (not LCD image)."""
    expression_id = max(1, min(35, int(expression_id)))
    msg = robot.set_expression(expression_id)
    return {"ok": msg.startswith("OK"), "message": msg}


@router.post("/display/show")
def display_show(text: str = "Rider Pi"):
    """
    POST /api/display/show – Zeigt Text auf dem physischen LCD (xgoscreen).
    Nur auf dem Pi mit installiertem xgoscreen. ?text=Ready oder text=Dein Text.
    """
    ok, msg = display_service.show_text_on_lcd(text=text or "Rider Pi")
    if not ok:
        raise HTTPException(status_code=503, detail=msg)
    return {"ok": True, "message": msg}


@router.post("/display/clear")
def display_clear():
    """POST /api/display/clear – Clear LCD to black."""
    ok, msg = display_service.clear_lcd()
    if not ok:
        raise HTTPException(status_code=503, detail=msg)
    return {"ok": True, "message": msg}


# Expression ID for "go!" dance (wiggle)
GO_DANCE_EXPRESSION_ID = 1


# Robot height: normal 95 mm, "up" 110 mm, "down" 88 mm (up-down per word)
HEIGHT_NORMAL_MM = 95
HEIGHT_UP_MM = 110
HEIGHT_DOWN_MM = 88


def _make_go_callback(expression_id: int):
    """Callback per word: robot moves up and down (height). On \"go!\": also dance (expression) + LED blink."""

    def _robot_word_action(word: str) -> None:
        r = deps.get_robot_optional()
        if r is None:
            return
        w = word.lower().replace("!", "").strip()
        is_go = w in ("go", "gooo")
        try:
            # Per word: robot briefly up, down, back (up-down motion)
            r.adjust_height(HEIGHT_UP_MM)
            time.sleep(0.22)
            r.adjust_height(HEIGHT_DOWN_MM)
            time.sleep(0.22)
            r.adjust_height(HEIGHT_NORMAL_MM)
            if is_go:
                logger.info("go!-Tanz: set_expression(%s) + LED-Blink", expression_id)
                r.set_expression(expression_id)
                for _ in range(6):
                    r.set_rgb(255, 0, 0)
                    time.sleep(0.2)
                    r.set_rgb(0, 0, 0)
                    time.sleep(0.2)
        except Exception as e:
            logger.warning("Robot Wort-Aktion fehlgeschlagen: %s", e, extra={"word": word})
            if is_go:
                logger.exception("go!-Tanz: %s", e)

    def _on_word(word: str, index: int) -> None:
        threading.Thread(
            target=_robot_word_action,
            args=(word,),
            daemon=True,
            name="robot_word_bounce",
        ).start()

    return _on_word


@router.post("/display/show_words")
def display_show_words(
    sentence: str = display_service.DEFAULT_WORDS_SENTENCE,
    delay: float = 1.0,
    loop: bool = False,
    go_expression: int = GO_DANCE_EXPRESSION_ID,
    robot: Optional[Any] = Depends(deps.get_robot_optional),
):
    """
    POST /api/display/show_words – sentence word by word on LCD. Text always centered.
    Robot moves up and down per word (height). On \"go!\": also dance (expression) + LED blink.
    go_expression: expression ID for "go!" (default 1). ?loop=1: endless loop; stop: POST /api/display/stop_words.
    """
    delay_sec = max(0.3, min(3.0, float(delay)))
    sent = sentence or display_service.DEFAULT_WORDS_SENTENCE
    expr_id = max(1, min(35, int(go_expression)))
    on_word = _make_go_callback(expr_id)

    if loop:
        ok, msg = display_service.start_words_loop(
            sentence=sent,
            delay_seconds=delay_sec,
            on_word=on_word,
        )
        if not ok:
            raise HTTPException(status_code=409, detail=msg)
        return JSONResponse(status_code=202, content={"ok": True, "message": msg})

    ok, msg = display_service.show_words_loop(
        sentence=sent,
        delay_seconds=delay_sec,
        on_word=on_word,
    )
    if not ok:
        raise HTTPException(status_code=503, detail=msg)
    return {"ok": True, "message": msg}


@router.post("/display/stop_words")
def display_stop_words():
    """POST /api/display/stop_words – Stoppt den laufenden Wort-Loop (show_words?loop=1)."""
    ok, msg = display_service.stop_words_loop()
    return {"ok": ok, "message": msg}


@router.post("/led")
def led(
    r: int = 255,
    g: int = 255,
    b: int = 255,
    robot: Any = Depends(_require_robot),
):
    """POST /api/led – RGB-LED (0–255)."""
    r = max(0, min(255, int(r)))
    g = max(0, min(255, int(g)))
    b = max(0, min(255, int(b)))
    msg = robot.set_rgb(r, g, b)
    return {"ok": msg.startswith("OK"), "message": msg}
