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
VIDEO_PORT = 5006
STATE_PORT = 5007

bot = Raspbot()
client_ip = None

pan_angle = 90
tilt_angle = 90
bot.Ctrl_Servo(1, 90)
bot.Ctrl_Servo(2, 90)

cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cmd_sock.bind(("0.0.0.0", CMD_PORT))
stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def command_listener():
    global client_ip, pan_angle, tilt_angle
    while True:
        data, addr = cmd_sock.recvfrom(4096)
        sender_ip, _ = addr
        if client_ip != sender_ip:
            client_ip = sender_ip
            print(f"Connected to laptop at {client_ip}")
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
            print(f"Camera opened (MJPG) on /dev/video0, shape={frame.shape}")
            return cap
    print("ERROR: Failed to read MJPG frame from /dev/video0")
    return None

def video_and_state_loop():
    cap = open_camera()
    sent_count = 0
    while True:
        if cap and client_ip:
            ret, frame = cap.read()
            if ret:
                _, jpeg = cv2.imencode(".jpg", frame, (int(cv2.IMWRITE_JPEG_QUALITY), 40))
                data = jpeg.tobytes()
                if len(data) < 60000:
                    stream_sock.sendto(data, (client_ip, VIDEO_PORT))
                    sent_count += 1
                    if sent_count % 50 == 1:
                        print(f"Sent frame #{sent_count} ({len(data)} bytes) to {client_ip}:{VIDEO_PORT}")
            else:
                print("WARNING: cap.read() returned False")

            state = {"pan": pan_angle, "tilt": tilt_angle}
            stream_sock.sendto(json.dumps(state).encode("utf-8"), (client_ip, STATE_PORT))

        time.sleep(0.04)

threading.Thread(target=command_listener, daemon=True).start()
print("Raspbot video & control bridge running...")
video_and_state_loop()
