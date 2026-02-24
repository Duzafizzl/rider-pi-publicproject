---
title: data README
description: Persistent data for the Rider Pi API – combos and map (initial state).
created: 2026-02-24
updated: 2026-02-24
---

# Data folder

This folder holds **persistent data** used by the API. The files start **empty** on purpose – they are filled at runtime or when you use the API.

| File | Purpose | Why empty? |
|------|---------|------------|
| **combos.json** | Saved movement combos (sequences). | No combos exist yet. Create them via `POST /api/combos` or the MCP tool `rider_pi_combo_execute`. |
| **map.json** | Rooms and landmarks (e.g. for future navigation). | Structure only; content is added when that feature is used. |

**combos.json** is read and written by the API; if it is missing, the server treats it as an empty list. **map.json** is a placeholder for optional map/navigation data.

You do not need to edit these files by hand. Use the API or MCP tools to create combos.
