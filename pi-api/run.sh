#!/usr/bin/env bash
# File: run.sh
# Description: Starts the Rider Pi API server (calls scripts/start.sh).
# Created: 2026-02-17
# Last updated: 2026-02-17

exec "$(dirname "$0")/scripts/start.sh"
