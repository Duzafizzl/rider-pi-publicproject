/**
 * File: ecosystem.config.cjs
 * Description: PM2 config for Rider Pi API. Autostart on boot.
 * Created: 2026-02-17
 * Last updated: 2026-02-24
 *
 * On the Pi (from the folder containing this file):
 *   ./scripts/setup_pm2_on_pi.sh
 * Or manually: pm2 start ecosystem.config.cjs && pm2 save && pm2 startup
 */

const path = require("path");

// Folder containing this config (e.g. ~/rider-pi-api on the Pi)
const appDir = __dirname;
// Use venv Python so installed deps (FastAPI, uvicorn, xgolib) are used. Create .venv first: python3 -m venv .venv && pip install -r requirements.txt
const venvPython = path.join(appDir, ".venv", "bin", "python");

module.exports = {
  apps: [
    {
      name: "rider-pi-api",
      script: "rider_pi_server.py",
      interpreter: venvPython,
      cwd: appDir,
      env: {
        HOST: "0.0.0.0",
        PORT: "5050",
      },
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: "5s",
      restart_delay: 3000,
      error_file: path.join(appDir, "logs", "pm2-err.log"),
      out_file: path.join(appDir, "logs", "pm2-out.log"),
    },
  ],
};
