import os
import socket
import json
import time
import threading
import cv2
from Raspbot_Lib import Raspbot

# Automatically stop Yahboom's default app so it doesn't block the camera/servos
os.system("pkill -f raspbot.pyc")
time.sleep(0.5)

# --- CONFIGURATION ---
CMD_PORT = 5005
VIDEO_PORT = 5006
STATE_PORT = 5007

bot = Raspbot()
client_ip = None

# Track current servo angles so students can read them back
servo_angles = {1: 90, 2: 90}
bot.Ctrl_Servo(1, 90)
bot.Ctrl_Servo(2, 90)

# Set up UDP sockets
cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cmd_sock.bind(("0.0.0.0", CMD_PORT))
stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def command_listener():
    """Listens for JSON commands from the student laptop."""
    global client_ip
    while True:
        data, addr = cmd_sock.recvfrom(4096)
        client_ip = addr[0]  # Lock onto the laptop's IP
        try:
            msg = json.loads(data.decode("utf-8"))
            cmd = msg.get("cmd")

            if cmd == "head":
                pan = int(max(0, min(180, msg.get("pan", 90))))
                tilt = int(max(0, min(180, msg.get("tilt", 90))))
                bot.Ctrl_Servo(1, pan)
                bot.Ctrl_Servo(2, tilt)
                servo_angles[1] = pan
                servo_angles[2] = tilt

            elif cmd == "color":
                # 0:Red, 1:Green, 2:Blue, 3:Yellow, 4:Purple, 5:Cyan, 6:White
                c = int(msg.get("color", 0))
                bot.Ctrl_WQ2812_ALL(1, c)

            elif cmd == "led_off":
                bot.Ctrl_WQ2812_ALL(0, 0)

            elif cmd == "move":
                # Motors 0,1 (Left) and 2,3 (Right), speed -255 to 255
                speeds = msg.get("speeds", [0, 0, 0, 0])
                for m_id, spd in enumerate(speeds[:4]):
                    spd = int(max(-255, min(255, spd)))
                    direction = 0 if spd >= 0 else 1
                    bot.Ctrl_Muto(m_id, direction, abs(spd))

            elif cmd == "beep":
                state = 1 if msg.get("on", False) else 0
                bot.Ctrl_BEEP_Switch(state)

        except Exception as e:
            print("Command error:", e)

def video_and_state_loop():
    """Streams camera frames and sensor state to the laptop."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    while True:
        ret, frame = cap.read()
        if ret and client_ip:
            # Compress frame to fit cleanly inside a single UDP packet
            _, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            data = jpeg.tobytes()
            if len(data) < 60000:
                stream_sock.sendto(data, (client_ip, VIDEO_PORT))

            # Send current servo angles & ultrasonic distance
            state = {
                "pan": servo_angles[1],
                "tilt": servo_angles[2],
            }
            stream_sock.sendto(json.dumps(state).encode("utf-8"), (client_ip, STATE_PORT))

        time.sleep(0.04)  # ~25 FPS

threading.Thread(target=command_listener, daemon=True).start()
print("Raspbot video & control bridge running...")
video_and_state_loop()
