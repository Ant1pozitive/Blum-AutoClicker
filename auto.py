import cv2
import numpy as np
import pyautogui
import mss
import time

# Диапазоны для цветков
FLOWER_HSV_RANGES = [
    {'lower': np.array([30, 100, 180]), 'upper': np.array([60, 255, 255])},
]

# Диапазоны для заморозок
FREEZE_HSV_RANGES = [
    {'lower': np.array([85, 20, 200]), 'upper': np.array([106, 140, 255])},
]

# Диапазоны для бомб
BOMB_HSV_RANGES = [
    {'lower': np.array([0, 3, 126]), 'upper': np.array([10, 22, 204])},
    {'lower': np.array([150, 3, 189]), 'upper': np.array([166, 22, 243])},
    {'lower': np.array([13, 9, 185]), 'upper': np.array([17, 10, 198])},
]

MIN_AREA = 200

# Область экрана, где находится игра
REGION = {'top': 195, 'left': 784, 'width': 373, 'height': 687}

MAX_CLICKS_PER_ITERATION = 5
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

def capture_screen(sct, region=None):
    screenshot = sct.grab(region)
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

def create_mask(img, hsv_ranges):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = None
    for range in hsv_ranges:
        lower = range['lower']
        upper = range['upper']
        current_mask = cv2.inRange(hsv, lower, upper)
        if mask is None:
            mask = current_mask
        else:
            mask = cv2.bitwise_or(mask, current_mask)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
    return mask

def find_contours(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_positions(contours, min_area):
    positions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            x_center = x + w // 2
            y_center = y + h // 2
            positions.append((x_center, y_center))
    return positions

def filter_safe_positions(positions, bomb_positions, min_distance=50):
    if not bomb_positions:
        return positions
    positions = np.array(positions)
    bomb_positions = np.array(bomb_positions)
    if positions.ndim == 1:
        if len(positions) == 2:
            positions = positions.reshape(1, 2)
        else:
            return []
    if bomb_positions.ndim == 1:
        if len(bomb_positions) == 2:
            bomb_positions = bomb_positions.reshape(1, 2)
        else:
            return positions

    diff = positions[:, np.newaxis, :] - bomb_positions[np.newaxis, :, :]
    distances = np.linalg.norm(diff, axis=2)
    min_distances = distances.min(axis=1)
    safe_positions = positions[min_distances > min_distance]

    return safe_positions.tolist()

def click_positions(positions, region_top_left):
    if not positions:
        return
    for pos in positions[:MAX_CLICKS_PER_ITERATION]:
        x = pos[0] + region_top_left['left']
        y = pos[1] + region_top_left['top']
        try:
            pyautogui.moveTo(x, y, duration=0.001)
            pyautogui.click()
        except Exception as e:
            pass

def main():
    print("Запуск скрипта автоматического клика на цветочки...")
    print("Нажмите 'q' для выхода.")
    with mss.mss() as sct:
        while True:
            start_time = time.time()
            img = capture_screen(sct, REGION)
            mask_bombs = create_mask(img, BOMB_HSV_RANGES)
            mask_flowers = create_mask(img, FLOWER_HSV_RANGES)
            mask_flowers = cv2.bitwise_and(mask_flowers, cv2.bitwise_not(mask_bombs))
            contours_flowers = find_contours(mask_flowers)
            contours_bombs = find_contours(mask_bombs)
            positions_flowers = get_positions(contours_flowers, MIN_AREA)
            positions_bombs = get_positions(contours_bombs, MIN_AREA)
            all_positions = positions_flowers
            safe_positions = filter_safe_positions(all_positions, positions_bombs, min_distance=50)
            click_positions(safe_positions, REGION)
            try:
                import keyboard
                if keyboard.is_pressed('q'):
                    print("Выход из скрипта.")
                    break
            except ImportError:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            end_time = time.time()
            elapsed = end_time - start_time
            if elapsed < 1 / 60:
                time.sleep((1 / 60) - elapsed)


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
