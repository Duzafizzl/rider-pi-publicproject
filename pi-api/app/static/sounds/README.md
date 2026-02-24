---
title: sounds README
description: Optional cue sounds for Rider Pi (listening ping, captured confirmation).
created: 2026-02-18
updated: 2026-02-24
---

# Audio cues (ping sounds)

Optional short sounds for the Rider Pi. If the files are placed here, they are played on `POST /api/audio/cue` with `cue=listening` or `cue=captured`.

| File | When |
|------|------|
| `listening.mp3` | When the rider enters listen mode. |
| `captured.mp3` | After a voice capture (capture confirmed). |

**Without these files:** A fallback beep is generated via ffmpeg (listening: 880 Hz, 0.15 s; captured: 660 Hz, 0.2 s).

Recommendation: Short, quiet clips (under 0.5 s), e.g. a soft tone or subtle “pling”.
