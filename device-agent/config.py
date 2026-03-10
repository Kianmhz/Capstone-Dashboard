"""
device-agent/config.py
======================
Edit this file on each machine before running agent.py.
"""

# ── Identity ──────────────────────────────────────────────────────────────────

# Human-readable name shown in the dashboard status badge
DEVICE_NAME = "Home PC"          # Change to "Raspberry Pi" on the Pi

# ── Network ───────────────────────────────────────────────────────────────────

# Port the agent listens on
PORT = 8001

# ── Program ───────────────────────────────────────────────────────────────────

# The command to launch your actual program.
# Can be a string (passed to shell) or a list (preferred, no shell).
#
# Examples:
#   PROGRAM_CMD = ["python", "main.py"]
#   PROGRAM_CMD = ["./my_binary", "--flag"]
#   PROGRAM_CMD = "cd /home/pi/project && python main.py"  # shell string

PROGRAM_CMD = ["python", "your_program.py"]   # ← change this

# ── Camera ────────────────────────────────────────────────────────────────────

# Camera backend: "opencv" or "picamera2" (Pi only) or "dummy"
# "dummy" streams a simple test pattern — useful for demos without real hardware
CAMERA_BACKEND = "opencv"

# OpenCV camera index (0 = first webcam)
OPENCV_CAMERA_INDEX = 0

# MJPEG stream frame rate (frames per second)
CAMERA_FPS = 15

# JPEG compression quality (1–100)
CAMERA_QUALITY = 70
