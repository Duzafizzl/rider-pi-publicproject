#!/usr/bin/env bash
# File: setup_pm2_on_pi.sh
# Description: Sets up PM2 on the Rider Pi (rider-pi-api autostart on boot). Run on the Pi.
# Created: 2026-02-17
# Last updated: 2026-02-24
#
# On the Pi: cd ~/rider-pi-api && ./scripts/setup_pm2_on_pi.sh
# Or from your PC: ssh pi@riderpi.local 'cd ~/rider-pi-api && ./scripts/setup_pm2_on_pi.sh'

set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
LOG_DIR="$ROOT/logs"
mkdir -p "$LOG_DIR"

echo "=== PM2 setup for rider-pi-api (Rider Pi) ==="

# Node/npm available?
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js not found. Installing Node.js (for PM2)..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y nodejs npm || true
  fi
  if ! command -v node >/dev/null 2>&1; then
    echo "Please install Node.js manually (e.g. from nodejs.org or: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs)"
    exit 1
  fi
fi

echo "Node: $(node -v)  npm: $(npm -v)"

# Install PM2 globally
if ! command -v pm2 >/dev/null 2>&1; then
  echo "Installing PM2 globally..."
  sudo npm install -g pm2
fi
echo "PM2: $(pm2 -v)"

# Stop old systemd unit if active (avoid double start)
if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet rider-pi-api 2>/dev/null; then
  echo "Stopping systemd rider-pi-api (switching to PM2)..."
  sudo systemctl stop rider-pi-api || true
  sudo systemctl disable rider-pi-api 2>/dev/null || true
fi

# PM2: start or reload app
if pm2 describe rider-pi-api >/dev/null 2>&1; then
  echo "rider-pi-api already in PM2 – reloading..."
  pm2 reload ecosystem.config.cjs
else
  echo "Starting rider-pi-api with PM2..."
  pm2 start ecosystem.config.cjs
fi

# Autostart on boot
echo "Enabling PM2 autostart on boot..."
pm2 save
sudo env PATH="$PATH" pm2 startup systemd -u pi --hp /home/pi 2>/dev/null || true

echo ""
echo "=== Status ==="
pm2 list
echo ""
echo "Done. rider-pi-api will now start on Rider Pi boot."
echo "Commands: pm2 status | pm2 logs rider-pi-api | pm2 restart rider-pi-api"
