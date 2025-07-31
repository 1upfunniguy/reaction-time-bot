import dxcam
import numpy as np
import pyautogui
import time
import keyboard

target_colors = [
    (244, 64, 68),
    (141, 218, 91),
    (232, 195, 149),
]

reset_colors = [
    (75, 219, 106),
    (206, 38, 54),
]

region = (0, 48, 1920, 588)

print("Press Ctrl+F6 to start.")
while not keyboard.is_pressed("ctrl+f6"):
    time.sleep(0.05)

camera = dxcam.create(output_idx=0, region=region)
camera.start(target_fps=0, video_mode=True)

print("Started. Press Ctrl+F6 again to stop.")

last_click_time = 0
cooldown = 0.05
last_reset_color_seen = time.time()

try:
    while True:
        if keyboard.is_pressed("ctrl+f6"):
            print("Ctrl+F6 detected, stopping.")
            break

        frame = camera.get_latest_frame()
        if frame is None:
            continue

        mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=bool)
        reset_color_detected = False

        for b, g, r in target_colors:
            color_mask = (frame[:, :, 0] == b) & (frame[:, :, 1] == g) & (frame[:, :, 2] == r)
            mask |= color_mask

        for rb, rg, rr in reset_colors:
            reset_mask = (frame[:, :, 0] == rb) & (frame[:, :, 1] == rg) & (frame[:, :, 2] == rr)
            if np.any(reset_mask):
                reset_color_detected = True
                last_reset_color_seen = time.time()
                break

        if np.any(mask):
            y_coords, x_coords = np.where(mask)
            top_idx = np.argmin(y_coords)
            x = x_coords[top_idx]
            y = y_coords[top_idx]

            now = time.time()
            if now - last_click_time > cooldown:
                pyautogui.click(region[0] + x, region[1] + y)
                last_click_time = now

except KeyboardInterrupt:
    print("Interrupted manually.")
finally:
    camera.stop()
    print("Stopped cleanly.")
