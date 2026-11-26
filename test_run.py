import time
import cv2
from raspbot_client_socket import RemoteRaspbot

bot = RemoteRaspbot("192.168.1.11")  # Replace with robot IP
step = 0

while True:
    frame = bot.get_camera()
    if frame is not None:
        cv2.imshow("Raspbot Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        pass
    else:
        print("No Frame");
        pass;

    # Gently nod left/right and toggle Blue/Green LEDs every ~1 second
    if step % 25 == 0:
        if (step // 25) % 2 == 0:
            bot.move_head(pan=115, tilt=30)
            bot.set_color(2)  # Blue
        else:
            bot.move_head(pan=65, tilt=30)
            bot.set_color(1)  # Green

    step += 1
    time.sleep(0.04)

    pass;
print("Finished! Nose up!")

bot.move_head(90, 90)
bot.led_off()
cv2.destroyAllWindows()
