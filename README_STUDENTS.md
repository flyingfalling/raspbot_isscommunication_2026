# Raspbot V2 Student Quick-Start Guide

## 1. Clone Repo & Set Up Python Virtual Environment
Open your terminal (macOS/Linux) or PowerShell/Git Bash (Windows) and run:

```bash
git clone <YOUR_REPO_URL>
cd raspbot_isscommunication_2026

# Create virtual environment
python3 -m venv raspi_venv

# Activate it:
# macOS / Linux:
source raspi_venv/bin/activate
# Windows (PowerShell):
.\raspi_venv\Scripts\Activate.ps1

# Install required packages (including our own)
pip install .
```

## 2. Connect to Your Robot
1. Turn on your Raspbot V2 and wait ~30 seconds for it to boot.
2. Connect your laptop's Wi-Fi to the robot's hotspot (`Raspbot-1` or `Raspbot-2`).
3. Read the IP address shown on the robot's small OLED screen (e.g., `192.168.1.99` or `192.168.1.100`).
4. Run the basic test script from the repository root:
   ```bash
   python test_run_ip.py 192.168.1.99
   ```
   *(Press `q` in the video window or `Ctrl+C` in the terminal to stop safely.)*

## 3. Running the Example Scripts (`examples/`)
Run any example:

* **Full API Tour (Head, LEDs, Beeps, Wheels):**
  `python examples/example_1_full_api_tour.py 192.168.1.99`
* **Acoustic & Visual Call Sender:**
  `python examples/example_2_acoustic_morse_sender.py 192.168.1.99`
* **Visual Color Tracker & Acoustic Responder:**
  `python examples/example_3_visual_receiver_tracker.py 192.168.1.99`
* **Interactive Keyboard Teleop (`W/A/S/D`, `I/J/K/L`, `B`, `1-6`):**
  `python examples/example_4_keyboard_teleop.py 192.168.1.99`

## 4. `RemoteRaspbot` API Reference
Import with `from robot_client_socket import RemoteRaspbot` and initialize `bot = RemoteRaspbot(robot_ip)`:

| Method | Parameters / Values | Description |
| :--- | :--- | :--- |
| `bot.get_camera()` | Returns `np.ndarray` or `None` | Latest `320x240` BGR OpenCV camera frame |
| `bot.get_angles()` | Returns `(pan, tilt)` | Current head servo angles in degrees |
| `bot.move_head(pan, tilt)` | `pan`: `0` (right) to `180` (left), `90` center<br>`tilt`: `0` (down) to `110` (up), **`30` level ahead** | Moves the 2-DOF camera head |
| `bot.set_color(color_id)` | `0`: Red, `1`: Green, `2`: Blue, `3`: Yellow,<br>`4`: Purple, `5`: Cyan, `6`: White | Sets the front RGB light bar |
| `bot.led_off()` | None | Turns off the RGB light bar |
| `bot.beep(on)` | `True` or `False` | Turns the onboard buzzer on or off |
| `bot.move_wheels(fl, rl, fr, rr)` | `-255` to `255` for each wheel<br>(Front-Left, Rear-Left, Front-Right, Rear-Right) | Controls the 4 Mecanum wheels |
| `bot.stop()` | None | Stops all 4 wheels immediately |
| `bot.close()` | None | Cleanly disconnects and resets hardware |
