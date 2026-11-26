import os
import time
import socket
import json
import threading
import cv2
from Raspbot_Lib import Raspbot

os.system("pkill -9 -f raspbot.pyc")
time.sleep(1.0)

CMD_PORT = 5005

bot = Raspbot()
client_addr = None
last_seen = 0.0
pan_angle = 90
tilt_angle = 30
bot.Ctrl_Servo(1, 90)
bot.Ctrl_Servo(2, 30)
#pan_angle = 90
#tilt_angle = 90
#bot.Ctrl_Servo(1, 90)
#bot.Ctrl_Servo(2, 90)

# Single socket handles BOTH receiving commands and replying with video/state
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", CMD_PORT))

def command_listener():
    global client_addr, last_seen, pan_angle, tilt_angle
    while True:
        data, addr = sock.recvfrom(4096)
        if client_addr != addr:
            print(f"Connected to laptop at {addr}")
        client_addr = addr
        last_seen = time.time()
        try:
            msg = json.loads(data.decode("utf-8"))
            cmd = msg.get("cmd")

            if cmd == "head":
                pan_angle = int(max(0, min(180, msg.get("pan", 90))))
                tilt_angle = int(max(0, min(180, msg.get("tilt", 90))))
                bot.Ctrl_Servo(1, pan_angle)
                bot.Ctrl_Servo(2, tilt_angle)

            elif cmd == "color":
                c = int(msg.get("color", 0))
                bot.Ctrl_WQ2812_ALL(1, c)

            elif cmd == "led_off":
                bot.Ctrl_WQ2812_ALL(0, 0)

            elif cmd == "move":
                speeds = msg.get("speeds", (0, 0, 0, 0))
                for m_id, spd in enumerate(tuple(speeds)[:4]):
                    spd = int(max(-255, min(255, spd)))
                    direction = 0 if spd >= 0 else 1
                    bot.Ctrl_Muto(m_id, direction, abs(spd))

            elif cmd == "beep":
                state = 1 if msg.get("on", False) else 0
                bot.Ctrl_BEEP_Switch(state)

        except Exception as e:
            print("Command error:", e)

def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 30)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"Camera opened (MJPG), shape={frame.shape}")
            return cap
    return None

def video_and_state_loop():
    global client_addr
    cap = open_camera()
    while True:
        # Automatically pause streaming 2 seconds after laptop stops sending
        if client_addr and (time.time() - last_seen > 2.0):
            print("Laptop disconnected (timeout). Waiting...")
            client_addr = None

        if cap and client_addr:
            ret, frame = cap.read()
            if ret:
                # Resize explicitly in OpenCV so UDP packet stays ~8-12 KB
                small = cv2.resize(frame, (320, 240))
                _, jpeg = cv2.imencode(".jpg", small, (int(cv2.IMWRITE_JPEG_QUALITY), 50))
                # Prefix 'V' for Video packet
                sock.sendto(b"V" + jpeg.tobytes(), client_addr)

            # Prefix 'S' for State packet
            state = json.dumps({"pan": pan_angle, "tilt": tilt_angle}).encode("utf-8")
            sock.sendto(b"S" + state, client_addr)

        time.sleep(0.04)

threading.Thread(target=command_listener, daemon=True).start()
print("Raspbot single-socket bridge running...")
video_and_state_loop()
