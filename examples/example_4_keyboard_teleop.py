import sys
import time
import cv2
from robot_client_socket import RemoteRaspbot

robot_ip = sys.argv.__getitem__(1) if len(sys.argv) > 1 else "192.168.1.99"
bot = RemoteRaspbot(robot_ip)

pan, tilt = 90, 30
print("Controls (click video window first): W/S=Drive, A/D=Turn, Q/E=Strafe, I/J/K/L=Head, B=Beep, 1-6=LED, Space=Stop, ESC=Quit")

try:
    while True:
        frame = bot.get_camera()
        if frame is not None:
            cv2.imshow(f"Teleop ({robot_ip})", frame)

        key = cv2.waitKey(30) & 0xFF
        if key == 27:
            break
        elif key == ord("w"):
            bot.move_wheels(100, 100, 100, 100)
        elif key == ord("s"):
            bot.move_wheels(-100, -100, -100, -100)
        elif key == ord("a"):
            bot.move_wheels(-90, -90, 90, 90)
        elif key == ord("d"):
            bot.move_wheels(90, 90, -90, -90)
        elif key == ord("q"):
            bot.move_wheels(-100, 100, 100, -100)
        elif key == ord("e"):
            bot.move_wheels(100, -100, -100, 100)
        elif key == ord(" "):
            bot.stop()
        elif key == ord("j"):
            pan = min(180, pan + 10); bot.move_head(pan, tilt)
        elif key == ord("l"):
            pan = max(0, pan - 10); bot.move_head(pan, tilt)
        elif key == ord("i"):
            tilt = min(110, tilt + 10); bot.move_head(pan, tilt)
        elif key == ord("k"):
            tilt = max(0, tilt - 10); bot.move_head(pan, tilt)
        elif key == ord("b"):
            bot.beep(True); time.sleep(0.1); bot.beep(False)
        elif ord("1") <= key <= ord("6"):
            bot.set_color(key - ord("1"))
        elif key == ord("0"):
            bot.led_off()
finally:
    bot.close()
    cv2.destroyAllWindows()
