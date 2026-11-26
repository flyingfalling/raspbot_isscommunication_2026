import sys
import time
import cv2
from robot_client_socket import RemoteRaspbot

robot_ip = sys.argv.__getitem__(1) if len(sys.argv) > 1 else "192.168.1.99"
bot = RemoteRaspbot(robot_ip)

VOCABULARY = {
    "ALERT":  (0, 90,  (0.1, 0.1, 0.1)),
    "GREET":  (1, 120, (0.4, 0.1)),
    "SEARCH": (5, 60,  (0.25, 0.25)),
}

def emit_signal(symbol_name):
    color_id, pan, pulses = VOCABULARY.get(symbol_name)
    print(f"Emitting signal: {symbol_name}")
    bot.set_color(color_id)
    bot.move_head(pan=pan, tilt=35)
    for dur in pulses:
        bot.beep(True)
        time.sleep(dur)
        bot.beep(False)
        time.sleep(0.12)
    bot.led_off()
    bot.move_head(90, 30)

try:
    sequence = ("GREET", "SEARCH", "ALERT", "GREET")
    for call in sequence:
        frame = bot.get_camera()
        if frame is not None:
            cv2.imshow(f"Sender View ({robot_ip})", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        emit_signal(call)
        time.sleep(1.2)
finally:
    bot.close()
    cv2.destroyAllWindows()
