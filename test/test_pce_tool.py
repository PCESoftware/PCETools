import sys
import json
import os
import shutil
import functools
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pce.pce_tool import PCETools

"""
def test_overlay():
    # overlay old_1 onto old_0, and export them into combined.pdf
    input_file = os.path.join(os.path.dirname(__file__), "overlay_old.pdf")
    output_svg = os.path.join(os.path.dirname(__file__), "combined.svg")
    output_file = os.path.join(os.path.dirname(__file__), "combined.pdf")
    PCETools.overlay_page(input_file, input_file, output_svg, 0, 1, position=(20, 10))
    PCETools.svg_to_pdf(output_svg, output_file)

def test_mix():
    standard_form = os.path.join(os.path.dirname(__file__), "mix\\all.pdf")
    file_list = [os.path.join(os.path.dirname(__file__), f"mix\\{i}.pdf") for i in range(1, 5)]
    output_path = os.path.join(os.path.dirname(__file__), "mix\\final.pdf")
    PCETools.mix_patch(standard_form, file_list, output_path)

def test_find():
    output_path = os.path.join(os.path.dirname(__file__), "mix\\final.pdf")
    print(PCETools.return_markup_by_page(output_path, 1))

def test_find_color():
    standard_form = os.path.join(os.path.dirname(__file__), "mix\\all.pdf")
    print(PCETools.pdf_color_v2(standard_form, 0))
    new_file = os.path.join(os.path.dirname(__file__), "mix\\output.pdf")
    PCETools.pdf_set_color_v2(standard_form, [0], "#0000ff", "#000000", new_file)
    new_file = os.path.join(os.path.dirname(__file__), "mix\\output_opacity_0.pdf")
    PCETools.pdf_set_color_v2(standard_form, [0], "#0000ff", "#000000", new_file, 0.0)

def test_copy_markup():
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup\\1.pdf")
    new_file = os.path.join(os.path.dirname(__file__), "copy_markup\\2.pdf")
    PCETools.paste_all_markup_to_file_by_anchor(standard_form, new_file)
    # PCETools.paste_all_markup_to_file_by_anchor_v2(standard_form, new_file)

def test_copy_markup_single():
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup\\1.pdf")
    markups = PCETools.return_markup_by_page(standard_form, 1)
    # content = [PCETools.copy_markup(standard_form, 1, markup) for markup, value in markups.items()]
    content = PCETools.copy_markup_v2(standard_form, 1, markups)
    print(content)

def test_offset():
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup\\1.pdf")
    new_file = os.path.join(os.path.dirname(__file__), "copy_markup\\2.pdf")
    print(PCETools.get_offset(standard_form, new_file))

def test_copy_markup():
    keys = ['PROJECT ADDRESS\r', 'MECHANICAL SERVICE\rXXXXXXX', 'XX', 'FOR APPROVAL', 'FY', '\r 1:XXX@A3', 'XXXXXXX', 'M-XXX', '   YYYYMMDD', 'FY', 'ISSUED FOR APPROVAL', '-', 'XX']
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_1.pdf")
    new_file = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_2.pdf")
    new_file_2 = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_backup.pdf")
    shutil.copy(new_file_2, new_file)
    PCETools.paste_markup_to_file(standard_form, new_file, content_replace_dict={"XXXXXXX": "Like this"})

def test_new_revision():
    region = [0, 802, 200, 11.5]
    region_2 = [0, 1611, 400, 11.5]
    region_3 = [0, 1611, 400, 11.5]
    new_region = region[:]
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_1.pdf")
    new_file = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_demo.pdf")
    new_file_markups = PCETools.return_markup_by_page(new_file, 1)
    while new_region[1] > 0 and PCETools.get_markup_in_region(new_file_markups, new_region) != {}:
        new_region[1] -= new_region[3]
    page_number = 1
    PCETools.paste_markup_to_file(standard_form, new_file, region=region, offset=(0, new_region[1] - region[1]))
    PCETools.set_replace(new_file, page_number, before=["FOR APPROVAL", "FOR CONSTRUCTION"], after="FOR APPROVAL")

def test_pdf_move_center():
    import multiprocessing
    center_point = [13.91296, 14.40692, 1161.803, 724.2948]
    pdf_file = os.path.join(os.path.dirname(__file__), "align_template\\Template_1.pdf")
    markups = PCETools.return_markup_by_page(pdf_file, 1)
    markups = PCETools.filter_markup_by(markups, {"color": "#7A0000"})
    assert len(markups) == 1
    markup_rect = list(markups.items())[0]
    coordinate = (float(markup_rect[1]['x']) + float(markup_rect[1]['width']) / 2, float(markup_rect[1]['y']) + float(markup_rect[1]['height']) / 2)
    center_coordinate = (center_point[0] + center_point[2] / 2, center_point[1] + center_point[3] / 2)

    offset = (center_coordinate[0] - coordinate[0], -center_coordinate[1] + coordinate[1])
    PCETools.set_markup(pdf_file, 1, {markup_rect[0]: {"x": str(center_coordinate[0] - float(markup_rect[1]['width']) / 2), "y": str(center_coordinate[1] - float(markup_rect[1]['height']) / 2)}})

    # pdf_file_2 = os.path.join(os.path.dirname(__file__), "align_template\\Template_2.pdf")
    # PCETools.pdf_content_move(pdf_file, pdf_file_2, offset)
    # shutil.move(pdf_file_2, pdf_file)
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(20)
    align_page_tmp = os.path.join(PCETools.TEMP_PATH, "align_page_tmp")
    os.makedirs(align_page_tmp, exist_ok=True)
    output_files = PCETools.split_pdf(pdf_file, align_page_tmp)
    output_files_2 = [item + ".output.pdf" for item in output_files]
    for _ in pool.starmap(PCETools.pdf_content_move, [(output_file, output_file_2, offset) for output_file, output_file_2 in zip(output_files, output_files_2)]):
        pass
    PCETools.combine_pdf(output_files_2, pdf_file)
    shutil.rmtree(align_page_tmp)

def mix_patch_v2(pdf_file, sub_files):
    import multiprocessing
    markups = PCETools.return_markup_by_page(pdf_file, 1)
    markup_color_position = {v["color"]: (float(v.get("x", 0.0)), float(v.get("y", 0.0))) for _, v in markups.items() if "color" in v}
    for pdf_file_i in sub_files:
        for page in range(PCETools.page_count(pdf_file_i)):
            markups_i = PCETools.return_markup_by_page(pdf_file_i, page + 1)
            markups_i = PCETools.filter_markup_by(markups_i, {"color": list(markup_color_position)})
            assert len(markups_i) == 1
            markup_i = list(markups_i.items())[0]
            coordinate = (float(markup_i[1]['x']), float(markup_i[1]['y']))
            pos = markup_color_position[markup_i[1]['color']]
            offset = (pos[0] - coordinate[0], coordinate[1] - pos[1])
            PCETools.set_markup(pdf_file_i, page + 1, {markup_i[0]: {"x": str(pos[0]), "y": str(pos[1])}})

        multiprocessing.freeze_support()
        pool = multiprocessing.Pool(20)
        align_page_tmp = os.path.join(PCETools.TEMP_PATH, "mix_patch_v2_tmp")
        os.makedirs(align_page_tmp, exist_ok=True)
        output_files = PCETools.split_pdf(pdf_file_i, align_page_tmp)
        output_files_2 = [item + ".output.pdf" for item in output_files]
        for _ in pool.starmap(PCETools.pdf_content_move, [(output_file, output_file_2, offset) for output_file, output_file_2 in zip(output_files, output_files_2)]):
            pass
        PCETools.combine_pdf(output_files_2, pdf_file_i)
        shutil.rmtree(align_page_tmp)

def test_mix_patch_v2():
    pdf_file = os.path.join(os.path.dirname(__file__), "mix\\all.pdf")
    pdf_file_i = [os.path.join(os.path.dirname(__file__), f"mix\\{i}.pdf") for i in range(1, 5)]
    mix_patch_v2(pdf_file, pdf_file_i)
"""

def test_version_setter():
    UPLIFT_SIZE = -11.6
    CONTEXT = {"a0": {"VERSION": {"$TYPE": "while-list", "$UPLIFT_SIZE": (0, UPLIFT_SIZE), "REV": [49.91895, 2318.24], "REVISION DESCRIPTION": [85.23486, 2318.24], "DRW": [227.1118, 2318.24], "CHK": [264.9587, 2318.24], "DATE Y.M.D": [304.6389, 2318.24]}, "PROJECT": [2272.446, 2232.563], "SCALE": [3053.2, 2235.87], "PROJECT No.": [3053.2, 2279.353], "DRAWING No.": [3053.2, 2320.773], "TYPE OF ISSUE": [3138.28, 2320.818], "DRAWN BY": [3138.28, 2236.499], "CHECKED BY": [3138.28, 2279.191]}, "a1": {"VERSION": {"$TYPE": "while-list", "$UPLIFT_SIZE": (0, UPLIFT_SIZE), "REV": [51.47995, 1617.341], "REVISION DESCRIPTION": [86.79601, 1617.341], "DRW": [228.6728, 1617.341], "CHK": [266.5199, 1617.341], "DATE Y.M.D": [306.1994, 1617.341]}, "PROJECT": [1524.801, 1533.359], "SCALE": [2067.0, 1535.052], "PROJECT No.": [2067.0, 1578.535], "DRAWING No.": [2067.0, 1619.956], "TYPE OF ISSUE": [2152.08, 1620.0], "DRAWN BY": [2152.08, 1535.682], "CHECKED BY": [2152.08, 1578.373]}, "a3": {"VERSION": {"$TYPE": "while-list", "$UPLIFT_SIZE": (0, UPLIFT_SIZE), "REV": [16.01697, 808.8484], "REVISION DESCRIPTION": [34.50598, 808.8484], "DRW": [142.6079, 808.8484], "CHK": [160.26, 808.8484], "DATE Y.M.D": [181.502, 808.8484]}, "PROJECT": [869.0056, 747.4893], "SCALE": [1075.596, 747.387], "PROJECT No.": [1079.934, 771.3923], "DRAWING No.": [1084.874, 794.3511], "TYPE OF ISSUE": [1084.786, 815.5005], "DRAWN BY": [1141.957, 748.9429], "CHECKED BY": [1143.425, 771.4201]}}
    TOL = 6
    pdf_file = os.path.join(os.path.dirname(__file__), "markup_version\\a3.pdf")
    markups = PCETools.return_markup_by_page(pdf_file, 1)
    structured_context = PCETools.get_structured_markups_from(markups, CONTEXT["a3"], TOL)
    new_line = {"REV":["",[0,0,"D"]],"REVISION DESCRIPTION":["",[34.50598,808.8484,"FOR CONSTRUCTION"]],"DRW":["",[142.6079,808.8484,"YX"]],"CHK":["",[0,0,"FY"]],"DATE Y.M.D":["",[181.502,808.8484,"20240830"]]}
    DATA_A = {"VERSION": structured_context["VERSION"], "PROJECT":["VTEEWTAAIDLFTHAP",[869.0056,747.4893,"299 Sussex St"]],"SCALE":["OBHMQOQPTKPYILCW",[1075.596,747.387,"1:1000000"]],"PROJECT No.":["WNHCNQNOOAEPUSUN",[1079.934,771.3923,"00233"]],"DRAWING No.":["MAIEOBPIPHPVHLGM",[1084.874,794.3511,"09874"]],"TYPE OF ISSUE":["RJAGNINEVSPMQEEO",[1084.786,815.5005,"Bill"]],"DRAWN BY":["WLBEZUIWNGGJEGNT",[1141.957,748.9429,"Hello"]],"CHECKED BY":["EIGQDLSYXVPYNYMR",[1143.425,771.4201,"Boss"]]}
    DATA_A["VERSION"].append(new_line)
    PCETools.set_structured_markups(pdf_file, 1, DATA_A, (0, UPLIFT_SIZE))