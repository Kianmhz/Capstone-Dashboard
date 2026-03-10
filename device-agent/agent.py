"""
device-agent/agent.py
=====================
Lightweight HTTP agent that runs on each device (PC or Raspberry Pi).
The Nuxt dashboard calls this agent to start/stop the local program
and to stream a video feed.

Endpoints
---------
  GET  /status       → { online, running, name }
  POST /start        → { success, message }
  POST /stop         → { success, message }
  GET  /video_feed   → MJPEG stream

Configuration
-------------
  All settings are in config.py (same directory).

Usage
-----
  pip install -r requirements.txt
  python agent.py
"""

import threading
import subprocess
import time
import logging
from flask import Flask, jsonify, Response
from flask_cors import CORS

import config
import camera

# ── logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── app setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)  # Allow dashboard origin (proxied through Nuxt anyway)

# ── process state ────────────────────────────────────────────────────────────

_process: subprocess.Popen | None = None
_process_lock = threading.Lock()


def _is_running() -> bool:
    """Return True if the managed process is alive."""
    with _process_lock:
        return _process is not None and _process.poll() is None


# ── routes ───────────────────────────────────────────────────────────────────

@app.get("/status")
def status():
    return jsonify({
        "online":  True,
        "running": _is_running(),
        "name":    config.DEVICE_NAME,
    })


@app.post("/start")
def start():
    global _process
    if _is_running():
        return jsonify({"success": False, "message": "Already running"})

    try:
        with _process_lock:
            log.info("Starting program: %s", config.PROGRAM_CMD)
            _process = subprocess.Popen(
                config.PROGRAM_CMD,
                shell=isinstance(config.PROGRAM_CMD, str),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        # Give it a moment to fail fast (e.g. file not found)
        time.sleep(0.3)
        if not _is_running():
            return jsonify({"success": False, "message": "Process exited immediately — check PROGRAM_CMD in config.py"})

        log.info("Program started (pid %d)", _process.pid)
        return jsonify({"success": True, "message": f"Started (pid {_process.pid})"})

    except Exception as exc:
        log.exception("Failed to start program")
        return jsonify({"success": False, "message": str(exc)}), 500


@app.post("/stop")
def stop():
    global _process
    if not _is_running():
        return jsonify({"success": False, "message": "Not running"})

    try:
        with _process_lock:
            log.info("Stopping program (pid %d)", _process.pid)
            _process.terminate()
            try:
                _process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _process.kill()
                _process.wait()
            _process = None

        log.info("Program stopped")
        return jsonify({"success": True, "message": "Stopped"})

    except Exception as exc:
        log.exception("Failed to stop program")
        return jsonify({"success": False, "message": str(exc)}), 500


@app.get("/video_feed")
def video_feed():
    """Stream MJPEG frames from the camera module."""
    return Response(
        camera.generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ── entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Starting agent '%s' on port %d", config.DEVICE_NAME, config.PORT)
    app.run(host="0.0.0.0", port=config.PORT, threaded=True)
