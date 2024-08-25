import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pce.simulator import Simulator

# def test_simulate_copy_and_write():
#     file_path_a = os.path.join(os.path.dirname(__file__), "copy_markup\\2.pdf")
#     file_path_b = os.path.join(os.path.dirname(__file__), "copy_markup\\1.pdf")
#     Simulator.copy_and_write(file_path_a, file_path_b)


# def test_simulate_click_4_points():
#     standard_form = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_empty.pdf")
#     points = (374, 575), (1860, 1625)
#     points = Simulator.get_rect(standard_form, points, page_number=1, color=None)
#     import time
#     time.sleep(3)
#     sim = Simulator()
#     for point in points:
#         sim.click_at(point)
# 
# def test_simulator_color():
#     colors = Simulator.get_color()
#     for color in colors:
#         print(color, end=' ')
#         print("#{:02X}{:02X}{:02X}".format(*color[:3]), end=' ')
#         print(colors[color])
