import socket
import json
import threading
import numpy as np
import cv2

class RemoteRaspbot:
    def __init__(self, robot_ip, cmd_port=5005, video_port=5006, state_port=5007):
        self.robot_ip = robot_ip
        self.cmd_port = cmd_port
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.latest_frame = None
        self.latest_state = {"pan": 90, "tilt": 90}

        self.vid_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vid_sock.bind(("0.0.0.0", video_port))
        threading.Thread(target=self._recv_video, daemon=True).start()

        self.state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.state_sock.bind(("0.0.0.0", state_port))
        threading.Thread(target=self._recv_state, daemon=True).start()

        self.move_head(90, 90)

    def _send(self, payload):
        self.cmd_sock.sendto(json.dumps(payload).encode("utf-8"), (self.robot_ip, self.cmd_port))

    def _recv_video(self):
        while True:
            data, _ = self.vid_sock.recvfrom(65535)
            arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is not None:
                self.latest_frame = frame

    def _recv_state(self):
        while True:
            data, _ = self.state_sock.recvfrom(4096)
            self.latest_state = json.loads(data.decode("utf-8"))

    def get_camera(self):
        return self.latest_frame

    def get_angles(self):
        return self.latest_state["pan"], self.latest_state["tilt"]

    def move_head(self, pan=90, tilt=90):
        self._send({"cmd": "head", "pan": pan, "tilt": tilt})

    def set_color(self, color_id):
        self._send({"cmd": "color", "color": color_id})

    def led_off(self):
        self._send({"cmd": "led_off"})

    def move_wheels(self, fl, rl, fr, rr):
        self._send({"cmd": "move", "speeds": [fl, rl, fr, rr]})

    def stop(self):
        self.move_wheels(0, 0, 0, 0)

    def beep(self, on=True):
        self._send({"cmd": "beep", "on": on})
