import sys
import time
import cv2
from robot_client_socket import RemoteRaspbot

# Use IP from command line if provided, otherwise default to 192.168.1.99
if (len(sys.argv) < 2 ):
    raise Exception("Requires IP addr argument of robot");

robot_ip = sys.argv[1];
print(f"Connecting to Raspbot at {robot_ip}...")

bot = RemoteRaspbot(robot_ip)
step = 0

while True:
    frame = bot.get_camera()
    if frame is not None:
        cv2.imshow(f"Raspbot ({robot_ip})", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    # Sweep left/right while keeping the camera level (tilt=30)
    if step % 25 == 0:
        if (step // 25) % 2 == 0:
            bot.move_head(pan=115, tilt=30)
            bot.set_color(2)  # Blue
        else:
            bot.move_head(pan=65, tilt=30)
            bot.set_color(1)  # Green

    step += 1
    time.sleep(0.04)

bot.move_head(90, 30)
bot.led_off()
cv2.destroyAllWindows()
