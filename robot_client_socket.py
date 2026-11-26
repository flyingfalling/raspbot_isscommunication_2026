import socket
import json
import time
import atexit
import threading
import numpy as np
import cv2

class RemoteRaspbot:
    def __init__(self, robot_ip, cmd_port=5005):
        self.robot_ip = robot_ip
        self.cmd_port = cmd_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._closed = False

        self.latest_frame = None
        self.latest_state = {"pan": 90, "tilt": 30}

        threading.Thread(target=self._recv_loop, daemon=True).start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        atexit.register(self.close)

        self.move_head(90, 30)

    def _send(self, payload):
        if not self._closed:
            try:
                self.sock.sendto(json.dumps(payload).encode("utf-8"), (self.robot_ip, self.cmd_port))
            except Exception:
                pass

    def _heartbeat_loop(self):
        while not self._closed:
            self._send({"cmd": "ping"})
            time.sleep(0.5)

    def _recv_loop(self):
        while not self._closed:
            try:
                data, _ = self.sock.recvfrom(65535)
                if not data:
                    continue
                if data[:1] == b"V":
                    arr = np.frombuffer(data[1:], dtype=np.uint8)
                    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        self.latest_frame = frame
                elif data[:1] == b"S":
                    self.latest_state = json.loads(data[1:].decode("utf-8"))
            except Exception:
                break

    def get_camera(self):
        return self.latest_frame

    def get_angles(self):
        return self.latest_state["pan"], self.latest_state["tilt"]

    def move_head(self, pan=90, tilt=30):
        self._send({"cmd": "head", "pan": pan, "tilt": tilt})

    def set_color(self, color_id):
        # 0:Red, 1:Green, 2:Blue, 3:Yellow, 4:Purple, 5:Cyan, 6:White
        self._send({"cmd": "color", "color": color_id})

    def led_off(self):
        self._send({"cmd": "led_off"})

    def move_wheels(self, fl, rl, fr, rr):
        self._send({"cmd": "move", "speeds": (fl, rl, fr, rr)})

    def stop(self):
        self.move_wheels(0, 0, 0, 0)

    def beep(self, on=True):
        self._send({"cmd": "beep", "on": on})

    def close(self):
        if not self._closed:
            self._send({"cmd": "disconnect"})
            self._closed = True
            try:
                self.sock.close()
            except Exception:
                pass
