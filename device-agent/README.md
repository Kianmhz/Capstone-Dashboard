# device-agent/README.md
# Device Agent

Lightweight Flask HTTP server that runs **locally on each machine** (PC and Pi).
The Nuxt dashboard calls this agent to control and monitor the device.

## Endpoints

| Method | Path | Response |
|---|---|---|
| `GET` | `/status` | `{ "online": true, "running": bool, "name": "..." }` |
| `POST` | `/start` | `{ "success": bool, "message": "..." }` |
| `POST` | `/stop` | `{ "success": bool, "message": "..." }` |
| `GET` | `/video_feed` | MJPEG stream |

## Setup

### 1. Install dependencies

```bash
cd device-agent
pip install -r requirements.txt
```

> On Raspberry Pi, `picamera2` is pre-installed on Raspberry Pi OS — skip installing it manually.

### 2. Configure the agent

Edit `config.py`:

```python
DEVICE_NAME    = "Home PC"          # or "Raspberry Pi"
PORT           = 8001
PROGRAM_CMD    = ["python", "your_program.py"]   # command to launch your program
CAMERA_BACKEND = "opencv"           # "opencv", "picamera2", or "dummy"
```

### 3. Run

```bash
python agent.py
```

The agent will be reachable at `http://<device-ip>:8001`.

---

## Camera backends

| Backend | Use when |
|---|---|
| `opencv` | USB webcam or built-in camera on PC or Pi |
| `picamera2` | Raspberry Pi camera module (CSI ribbon cable) |
| `dummy` | No camera — streams an animated test pattern (great for demos) |

---

## Running on boot (Raspberry Pi)

Create a systemd service so the agent starts automatically:

```bash
sudo nano /etc/systemd/system/capstone-agent.service
```

Paste:

```ini
[Unit]
Description=Capstone Device Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/Capstone-Dashboard/device-agent/agent.py
WorkingDirectory=/home/pi/Capstone-Dashboard/device-agent
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable capstone-agent
sudo systemctl start capstone-agent
sudo systemctl status capstone-agent
```
