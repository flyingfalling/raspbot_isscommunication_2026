import sys
import time
import numpy as np
import cv2
from robot_client_socket import RemoteRaspbot

robot_ip = sys.argv.__getitem__(1) if len(sys.argv) > 1 else "192.168.1.99"
bot = RemoteRaspbot(robot_ip)

pan = 90
last_response_time = 0

try:
    while True:
        frame = bot.get_camera()
        if frame is not None:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array((35, 80, 80), dtype=np.uint8)
            upper_green = np.array((85, 255, 255), dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_green, upper_green)
            green_pixels = cv2.countNonZero(mask)

            if green_pixels > 500:
                M = cv2.moments(mask)
                cx = int(M.get("m10") / M.get("m00"))
                _, width, _ = frame.shape
                error_x = cx - (width // 2)
                pan = int(max(10, min(170, pan - error_x * 0.05)))
                bot.move_head(pan=pan, tilt=30)
                bot.set_color(1)

                if time.time() - last_response_time > 2.0:
                    bot.beep(True)
                    time.sleep(0.1)
                    bot.beep(False)
                    last_response_time = time.time()
            else:
                bot.led_off()

            cv2.imshow(f"Receiver View ({robot_ip})", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time.sleep(0.04)
finally:
    bot.close()
    cv2.destroyAllWindows()
