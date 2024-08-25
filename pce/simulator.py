import pyautogui
import keyboard
import time
from .pce_tool import PCETools
import subprocess

class Simulator:
    def __init__(self):
        pass

    def type_text(self, text):
        for char in text:
            pyautogui.write(char)
            time.sleep(0.1)

    def click_at(self, position):
        x, y = position
        pyautogui.moveTo(x, y)
        time.sleep(0.5)
        pyautogui.click()

    @staticmethod
    def copy_and_write(file_path_a, file_path_b):
        pages = PCETools.page_count(file_path_a)
        print([f'"{PCETools.BLUEBEAM_DIR}"', f'{file_path_a} {file_path_b}'])
        subprocess.Popen(f'"{PCETools.BLUEBEAM_DIR}" {file_path_a} {file_path_b}', shell=True)
        position_doc, position_doc_2 = (385, 158), (445, 158)
        position_left, position_right = (1000, 500), (2500, 500)
        position_start, position_next = (1769, 2026), (2092, 2026)
        position_division = (415, 2023)
        position_close = (3820, 15)
        time.sleep(5)
        sim = Simulator()
        sim.click_at(position_doc)
        sim.click_at(position_division)
        time.sleep(1)
        sim.click_at(position_doc_2)
        time.sleep(1)
        sim.click_at(position_start)
        time.sleep(1)
        for i in range(pages):
            sim.click_at(position_left)
            keyboard.press_and_release('ctrl+a')
            keyboard.press_and_release('ctrl+c')
            # time.sleep(3)
            sim.click_at(position_right)
            keyboard.press_and_release('ctrl+shift+v')
            if i < pages - 1:
                time.sleep(5)
                sim.click_at(position_next)
                time.sleep(1)
            else:
                keyboard.press_and_release('ctrl+s')
                time.sleep(5)
                sim.click_at(position_close)

    @staticmethod
    def get_rect(file_path, two_point_position, page_number=1, color=None):
        (x1, y1), (x2, y2) = two_point_position
        dct = PCETools.return_markup_by_page(file_path, page_number)
        w, h = PCETools.page_size(file_path, page_number - 1)
        rect = [(k, v) for k, v in dct.items() if v.get("subject") == 'Rectangle']
        if color is not None:
            rect = [(k, v) for k, v in rect if rect['color'] == color]
        assert len(rect) == 1
        rect = rect[0][1]
        x, y, width, height, c = float(rect['x']), float(rect['y']), float(rect['width']), float(rect['height']), rect['color']
        a, b, c, d = (x, y), (x + width, y), (x + width, y + height), (x, y + height)
        a1, b1, c1, d1 = [(x1 + xi / w * (x2 - x1), y1 + yi / h * (y2 - y1)) for xi, yi in [a, b, c, d]]
        return a1, b1, c1, d1

    @staticmethod
    def get_color():
        time.sleep(3)
        data = pyautogui.screenshot()
        first_point, y_sampling_point, step = (1765, 815), (1750, 825), 33
        lines = 0
        while y_sampling_point[1] + step * lines < data.height:
            if data.getpixel((y_sampling_point[0], y_sampling_point[1] + step * lines)) != (255, 255, 255):
                break
            lines += 1
        lines -= 1
        res = {}
        for i in range(lines):
            for j in range(8):
                xy = (first_point[0] + step * j, first_point[1] + step * i)
                color = data.getpixel(xy)
                if color not in res:
                    res[color] = xy
        return res
