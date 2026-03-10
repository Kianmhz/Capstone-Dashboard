"""
device-agent/camera.py
======================
Camera abstraction that supports three backends:

  "opencv"    — any USB/built-in webcam via OpenCV (works on PC and Pi)
  "picamera2" — Raspberry Pi camera module (CSI ribbon cable)
  "dummy"     — animated test pattern, no hardware needed

The backend is selected by CAMERA_BACKEND in config.py.
"""

import time
import logging
import config

log = logging.getLogger(__name__)


# ── OpenCV backend ────────────────────────────────────────────────────────────

def _frames_opencv():
    import cv2
    cap = cv2.VideoCapture(config.OPENCV_CAMERA_INDEX)
    if not cap.isOpened():
        log.error("OpenCV: could not open camera index %d", config.OPENCV_CAMERA_INDEX)
        # Fall back to dummy so the stream doesn't crash
        yield from _frames_dummy()
        return

    delay = 1.0 / config.CAMERA_FPS
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                log.warning("OpenCV: failed to read frame, retrying…")
                time.sleep(0.5)
                continue
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, config.CAMERA_QUALITY])
            yield buf.tobytes()
            time.sleep(delay)
    finally:
        cap.release()


# ── Picamera2 backend (Raspberry Pi) ─────────────────────────────────────────

def _frames_picamera2():
    from picamera2 import Picamera2
    import io
    from PIL import Image

    cam = Picamera2()
    cam.configure(cam.create_video_configuration(main={"size": (640, 480)}))
    cam.start()
    delay = 1.0 / config.CAMERA_FPS

    try:
        while True:
            array = cam.capture_array()
            img = Image.fromarray(array)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=config.CAMERA_QUALITY)
            yield buf.getvalue()
            time.sleep(delay)
    finally:
        cam.stop()


# ── Dummy backend (animated test pattern) ─────────────────────────────────────

def _frames_dummy():
    """
    Generates a simple animated JPEG without any camera hardware.
    Uses only the standard library + Pillow.
    """
    from PIL import Image, ImageDraw, ImageFont
    import io

    delay = 1.0 / config.CAMERA_FPS
    frame_num = 0

    while True:
        img = Image.new("RGB", (640, 480), color=(15, 15, 30))
        draw = ImageDraw.Draw(img)

        # Animated bar
        bar_x = (frame_num * 4) % 640
        draw.rectangle([bar_x, 0, bar_x + 40, 480], fill=(0, 80, 180))

        # Labels
        draw.text((20, 20),  f"[ {config.DEVICE_NAME} ]",  fill=(0, 220, 120))
        draw.text((20, 50),  "VIDEO FEED — DUMMY MODE",     fill=(180, 180, 180))
        draw.text((20, 80),  time.strftime("%H:%M:%S"),     fill=(220, 220, 60))
        draw.text((20, 440), f"frame {frame_num}",          fill=(100, 100, 100))

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=config.CAMERA_QUALITY)
        yield buf.getvalue()

        frame_num += 1
        time.sleep(delay)


# ── Public generator ──────────────────────────────────────────────────────────

def generate_frames():
    """
    Yields MJPEG-formatted byte chunks for use in a Flask streaming response.
    Selects the backend from config.CAMERA_BACKEND.
    """
    backend = config.CAMERA_BACKEND.lower()

    if backend == "opencv":
        raw = _frames_opencv()
    elif backend == "picamera2":
        raw = _frames_picamera2()
    else:
        if backend != "dummy":
            log.warning("Unknown CAMERA_BACKEND '%s', falling back to dummy", backend)
        raw = _frames_dummy()

    for frame_bytes in raw:
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )
