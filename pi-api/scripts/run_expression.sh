#!/usr/bin/env bash
# File: run_expression.sh
# Description: Single test – POST /api/expression (LCD on robot: expression 1–35).
# Created: 2026-02-17
# Last updated: 2026-02-24
# Usage: ./scripts/run_expression.sh [expression_id]   (default: 1)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/config/.env" ] && set -a && . "$ROOT/config/.env" && set +a
BASE="http://${RIDER_PI_HOST:-riderpi.local}:5050"
ID="${1:-1}"

echo "→ POST $BASE/api/expression?expression_id=$ID (LCD should show expression $ID)"
curl -sf --connect-timeout 5 -X POST "$BASE/api/expression?expression_id=$ID" | python3 -m json.tool
echo ""
echo "Check: Do you see something on the robot's small display (no longer 'unconnected')?"
