import pyautogui
import time

print("Наведите курсор на верхний левый угол окна игры через 5 секунд...")
time.sleep(5)
x1, y1 = pyautogui.position()
print(f"Координаты верхнего левого угла: x={x1}, y={y1}")


print("Наведите курсор на нижний правый угол окна игры через 5 секунд...")
time.sleep(5)
x2, y2 = pyautogui.position()
print(f"Координаты нижнего правого угла: x={x2}, y={y2}")


width = x2 - x1
height = y2 - y1
print(f"Ширина: {width}, Высота: {height}")


region = {'top': y1, 'left': x1, 'width': width, 'height': height}
print(region)
