#!/usr/bin/env bash
# File: setup_pi_prompt.sh
# Description: Sets a colored shell prompt on the Pi (pi@raspberrypi:~$) so you can see: session = Pi, not Mac.
# Created: 2026-02-17
# Last updated: 2026-02-24
#
# Run once on the Pi:
#   Option A (from PC via SSH):  ssh pi@riderpi.local 'bash -s' < scripts/setup_pi_prompt.sh
#   Option B (after SSH to Pi):  bash ~/rider-pi-api/scripts/setup_pi_prompt.sh

MARKER="# rider-pi: colored prompt (Pi session)"
RC="${HOME}/.bashrc"

if grep -qF "$MARKER" "$RC" 2>/dev/null; then
  echo "Colored Pi prompt is already in $RC."
  exit 0
fi

# Yellow/orange: easy to see (remote session)
# \033[01;33m = bold yellow, \033[00m = reset
PROMPT_LINE='PS1='"'"'\[\033[01;33m\]\u@\h:\w\$ \[\033[00m\]'"'"'   # Pi session'
echo "" >> "$RC"
echo "$MARKER" >> "$RC"
echo "$PROMPT_LINE" >> "$RC"
echo "Colored Pi prompt added to $RC. Next session or: source $RC"
exit 0
