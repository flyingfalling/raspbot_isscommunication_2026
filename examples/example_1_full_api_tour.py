import sys
import time
import cv2
from robot_client_socket import RemoteRaspbot

robot_ip = sys.argv.__getitem__(1) if len(sys.argv) > 1 else "192.168.1.99"
bot = RemoteRaspbot(robot_ip)

def wait_with_video(seconds):
    end = time.time() + seconds
    while time.time() < end:
        frame = bot.get_camera()
        if frame is not None:
            pan, tilt = bot.get_angles()
            cv2.putText(frame, f"Pan:{pan} Tilt:{tilt}", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow(f"Full API Tour ({robot_ip})", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise KeyboardInterrupt
        time.sleep(0.03)

try:
    print("1. Sweeping head (pan & tilt)...")
    for pan, tilt in ((140, 30), (40, 30), (90, 70), (90, 10), (90, 30)):
        bot.move_head(pan=pan, tilt=tilt)
        wait_with_video(0.6)
        print("   Current angles:", bot.get_angles())

    print("2. Cycling all 7 RGB LED colors...")
    for color_id in range(7):
        bot.set_color(color_id)
        wait_with_video(0.4)
    bot.led_off()

    print("3. Testing acoustic buzzer chirps...")
    for _ in range(3):
        bot.beep(True)
        wait_with_video(0.12)
        bot.beep(False)
        wait_with_video(0.15)

    print("4. Testing Mecanum wheels (keep robot on floor!)...")
    bot.move_wheels(80, 80, 80, 80)
    wait_with_video(0.6)
    bot.move_wheels(-80, -80, -80, -80)
    wait_with_video(0.6)
    bot.move_wheels(90, -90, -90, 90)
    wait_with_video(0.6)
    bot.move_wheels(-90, -90, 90, 90)
    wait_with_video(0.6)

    bot.stop()
    print("Tour complete!")

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    bot.stop()
    bot.led_off()
    bot.beep(False)
    bot.move_head(90, 30)
    bot.close()
    cv2.destroyAllWindows()
