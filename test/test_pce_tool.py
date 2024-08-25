import sys
import os
import shutil
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
"""

def test_new_revision():
    region = [0, 802, 200, 11.5]
    new_region = region[:]
    standard_form = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_1.pdf")
    new_file = os.path.join(os.path.dirname(__file__), "copy_markup_image\\Drawing_2.pdf")
    new_file_markups = PCETools.return_markup_by_page(new_file, 1)
    while new_region[1] > 0 and PCETools.get_markup_in_region(new_file_markups, new_region) != {}:
        new_region[1] -= new_region[3]
    page_number = 1
    PCETools.paste_markup_to_file(standard_form, new_file, region=region, offset=(0, new_region[1] - region[1]))
    PCETools.set_replace(new_file, page_number, before=["FOR APPROVAL", "FOR CONSTRUCTION"], after="FOR APPROVAL")
