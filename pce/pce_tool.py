import uuid
import os
import shutil
import subprocess
import logging
import re
import io
import fitz
import svgwrite
from xml.etree import ElementTree as ET
import pypdf
import json

logger = logging.getLogger(__name__)
logging.basicConfig(filename='myapp.log', level=logging.INFO)

class External(svgwrite.container.Group):
    def __init__(self, xml, **extra):
        self.xml = xml
        ns = u'{http://www.w3.org/2000/svg}'
        nsl = len(ns)
        for elem in self.xml.iter():
            if elem.tag.startswith(ns):
                elem.tag = elem.tag[nsl:]

        super(External, self).__init__(**extra)

    def get_xml(self):
        return self.xml

class PCETools:
    BLUEBEAM_DIR = r"C:\Program Files\Bluebeam Software\Bluebeam Revu\2017\Revu\Revu.exe"
    BLUEBEAM_ENGINE_DIR = r"C:\Program Files\Bluebeam Software\Bluebeam Revu\2017\Script\ScriptEngine.exe"
    INKSCAPE_DIRECTORY = r"C:\Progra~1\Inkscape\bin\inkscape.exe"
    TEMP_PATH = r"D:\Workspace\repos\pce_tools"
    @classmethod
    def SetEnvironment(cls, BLUEBEAM_DIR, BLUEBEAM_ENGINE_DIR, INKSCAPE_DIRECTORY, TEMP_PATH):
        cls.BLUEBEAM_DIR = BLUEBEAM_DIR
        cls.BLUEBEAM_ENGINE_DIR = BLUEBEAM_ENGINE_DIR
        cls.INKSCAPE_DIRECTORY = INKSCAPE_DIRECTORY
        cls.TEMP_PATH = TEMP_PATH

    @staticmethod
    def _rename_id(element, suffix=None):
        if suffix is None:
            suffix = str(uuid.uuid4()).split('-')[0]
        for elem in element.iter():
            for key in elem.keys():
                if key in ('id', ):
                    elem.set(key, elem.get(key) + '_' + suffix)
            for key in elem.attrib:
                if re.match(r".*url\(#.*\).*", elem.attrib[key]):
                    elem.attrib[key] = re.sub(r"\(#(.*?)\)", r"(#{}_{})".format(r"\1", suffix), elem.attrib[key])
                if key.endswith("href") and re.match(r"#.*", elem.attrib[key]):
                    elem.attrib[key] = re.sub(r"#(.*)", r"#{}_{}".format(r"\1", suffix), elem.attrib[key])

    @staticmethod
    def pdf_page_to_svg(pdf_path, page_number, svg_file):
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        svg_image = page.get_svg_image()
        svg_image = svg_image.replace("&", "&amp;")
        svg_file.write(svg_image.encode('ascii'))

    @staticmethod
    def page_count(pdf_path):
        doc = fitz.open(pdf_path)
        return doc.page_count

    @staticmethod
    def page_size(pdf_path, page_id):
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_id)
        return (page.rect.width, page.rect.height)

    @staticmethod
    def _get_svg_bytes_from_pdf(file_name, page_number):
        with io.BytesIO() as write_buffer:
            PCETools.pdf_page_to_svg(file_name, page_number, write_buffer)
            write_buffer.seek(0)
            svg_file = write_buffer.read().decode('ascii')
        return svg_file

    @staticmethod
    def get_ET(file_name, page_number):
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        if file_name.endswith(".pdf"):
            svg_file = PCETools._get_svg_bytes_from_pdf(file_name, page_number)
        else:
            with open(file_name, 'r') as f:
                svg_file = f.read()
        root = ET.fromstring(svg_file)
        return root

    @staticmethod
    def ET_to_svg(root, svg_file):
        tree = ET.ElementTree(root)
        tree.write(svg_file)

    @staticmethod
    def overlay_page(file_name1, overlay, output_path, page_number=0, page_number_overlay=0, position=(10, 10)):
        background_root = PCETools.get_ET(file_name1, page_number)
        overlay_root = PCETools.get_ET(overlay, page_number_overlay)
        # avoid duplication of namespace
        PCETools._rename_id(overlay_root)

        # same size as background
        background_width = background_root.attrib.get('width', '100%')
        background_height = background_root.attrib.get('height', '100%')
        dwg = svgwrite.Drawing(output_path, size=(background_width, background_height))

        background_group = dwg.g(id='background')
        background_group.add(External(background_root))
        dwg.add(background_group)

        overlay_group = dwg.g(id='overlay', transform='translate(%f, %f)' % (position[0], position[1]))
        overlay_group.add(External(overlay_root))
        dwg.add(overlay_group)

        dwg.save()

    @staticmethod
    def merge_page(et_list, coordinate_list, page_size, output_path):
        for item_root in et_list[1:]:
            PCETools._rename_id(item_root)
        dwg = svgwrite.Drawing(output_path, size=page_size)
        for i, item in enumerate(et_list):
            group = dwg.g(id="svg_{}".format(i), transform='translate(%f, %f)' % (coordinate_list[i][0], coordinate_list[i][1]))
            group.add(External(item))
            dwg.add(group)
        dwg.save()

    @staticmethod
    def resize_pdf(input_file, input_scale, input_size_x, input_size_y, output_scale, output_size_x, output_size_y, output_dir):
        reader = pypdf.PdfReader(input_file)
        writer = pypdf.PdfWriter()
        page_scale_x = float(output_size_x) / float(input_size_x)
        page_scale_y = float(output_size_y) / float(input_size_y)
        content_scale_x = (float(input_scale) / float(output_scale)) / page_scale_x
        content_scale_y = (float(input_scale) / float(output_scale)) / page_scale_y
        op = pypdf.Transformation().scale(content_scale_x, content_scale_y)
        for page in reader.pages:
            if "/VP" in page.keys():
                page.pop("/VP")
            if page_scale_x != 1 or page_scale_y != 1:
                page.scale(page_scale_x, page_scale_y)

            if content_scale_x != 1 or content_scale_y != 1:
                page.add_transformation(op)
            writer.add_page(page)
        writer.write(output_dir)

    @staticmethod
    def svg_to_pdf(src, dest):
        command = [f'"{src}"', "--export-type=pdf", f'--export-filename="{dest}"']
        os.system(' '.join([f'{PCETools.INKSCAPE_DIRECTORY}'] + command))

    # Bluebeam
    @staticmethod
    def combine_pdf(input_file_list, output_file):
        if len(input_file_list) == 1:
            shutil.copy(input_file_list[0], output_file)
            return
        combine_pdfs = []
        for file in input_file_list:
            combine_pdfs.append('\'' + file + '\'')

        command = f"Combine({', '.join(combine_pdfs)}) Save('{output_file}') Close()"
        subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, command])

    @staticmethod
    def return_markup_by_page(file_dir, i):
        command = f"Open('{file_dir}') MarkupGetExList({i}) Close()"

        result_bytes = subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, command])
        result_text = result_bytes.decode("gbk").split("\n")[1]
        string = result_text.replace("|\"", "\"").replace("|'", "'").replace("'{", "{").replace("}'", "}").replace("||", "\\").replace("'True'", "true").replace("'False'", "false").replace("'None'", "null").replace("'", '"')
        result_json = json.loads(string)
        return result_json

    @staticmethod
    def get_markup_in_region(markups, region):
        # region should be in the format of [x, y, width, height]
        markups = {k: v for k, v in markups.items() if region[0] < float(v.get('x', -1)) < region[0] + region[2] and region[1] < float(v.get('y', -1)) < region[1] + region[3]}
        return markups

    @staticmethod
    def get_markup_with_content(markups, contents):
        if type(contents) is str:
            contents = [contents]
        contents = [item.lower() for item in contents]
        markups = {k: v for k, v in markups.items() if v.get("comment", '').strip().lower() in contents}
        return markups

    @staticmethod
    def filter_markup_by(markups, property_dict):
        for prop_k, prop_v in property_dict.items():
            if type(prop_v) != list:
                prop_v = [prop_v]
            markups = {k: v for k, v in markups.items() if v.get(prop_k) in prop_v}
        return markups

    @staticmethod
    def copy_markup(file_dir, i, key):
        command = f"Open('{file_dir}') MarkupCopy({i}, '{key}') Close()"
        result_bytes = subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, command])
        result_text = result_bytes.decode("utf-8").split("\n")[1].strip()
        return result_text

    @staticmethod
    def get_offset(standard_form, new_file, anchor_color="#7A0000", scale=(28.3463544, 28.3463544)):
        pages = PCETools.page_count(standard_form)
        assert pages == PCETools.page_count(new_file), "file page count mismatch"
        offsets = []
        for i in range(1, pages + 1):
            markups_1, markups_2 = PCETools.return_markup_by_page(standard_form, i), PCETools.return_markup_by_page(new_file, i)
            markups_1, markups_2 = [markup for markup in markups_1.values() if markup["color"].lower() == anchor_color.lower()], [markup for markup in markups_2.values() if markup["color"].lower() == anchor_color.lower()]
            assert len(markups_1) > 0 and len(markups_2) > 0, "expected markup with the color {}, but found ({}, {})".format(anchor_color, len(markups_1), len(markups_2))
            markup_1, markup_2 = markups_1[0], markups_2[0]
            offset = (float(markup_2['x']) - float(markup_1['x']), float(markup_2['y']) - float(markup_1['y']))
            offset = (offset[0] / scale[0], offset[1] / scale[1])
            offsets.append(offset)
        return offsets

    @staticmethod
    def copy_markup_batch(file_dir, i, dct):
        logger.info("page: {}, copy: {}".format(i, len(dct)))
        command = [f"Open('{file_dir}')", *[f"MarkupCopy({i}, '{key}')" for key in dct.keys()], "Close()"]
        with open("copy_markup.bci", 'w') as f:
            f.write('\n'.join(command))
        result_bytes = subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, "Script('copy_markup.bci')"])
        result_text = result_bytes.decode("utf-8").split("\r\n")[1::2]
        logger.info("page: {}, copy: {} result".format(i, len(result_text)))
        os.remove("copy_markup.bci")
        return result_text

    @staticmethod
    def paste_markup(file_dir, i, content, content_replace_dict=None):
        # paste
        logger.info("page: {}, paste: {}".format(i, len(content)))
        command = [f"Open('{file_dir}')"]
        for item in content:
            format_xml, position = item
            new_position = (position[1] + position[2], position[0]) if all([position[i] is not None for i in range(3)]) else (0, 0)
            command.append(f"MarkupPaste({i}, '{format_xml}', {new_position[0]}, {new_position[1]})")
        command.extend(["Save()", "Close()"])
        with open("paste_markup.bci", 'w') as f:
            f.write('\n'.join(command))
        markup_ids = subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, "Script('paste_markup.bci')"])
        markup_ids_result = [markup_id.strip() for markup_id in markup_ids.decode('utf-8').strip().split('\r\n')]
        line_id, markup_ids = 0, []
        while line_id < len(markup_ids_result):
            k = int(markup_ids_result[line_id])
            markup_ids.append(markup_ids_result[line_id + 1: line_id + 1 + k])
            line_id += 1 + k
        # set
        logger.info("paste_markup: page: {}, set: {}".format(i, len(markup_ids)))
        markup_setter = {}
        for item, markup_id in zip(content, markup_ids):
            if any([item[1][i] is None for i in range(3)]):
                continue
            markup_id = markup_id[0]
            markup_setter[markup_id] = {"x": str(item[1][0]), "y": str(item[1][1])}
            if content_replace_dict is not None and item[1][3] in content_replace_dict:
                markup_setter[markup_id]["comment"] = content_replace_dict[item[1][3]]
        PCETools.set_markup(file_dir, i, markup_setter)
        os.remove("paste_markup.bci")

    @staticmethod
    def set_markup(file_dir, i, markup_ids_dict):
        command = [f"Open('{file_dir}')"]
        for markup_id, cont in markup_ids_dict.items():
            command.append("MarkupSet({}, '{}', '{}')".format(i, markup_id, json.dumps(cont)))
        command.extend(["Save()", "Close()"])
        logger.info("paste_markup for page {} Complete.".format(i))
        with open("set_markup.bci", 'w') as f:
            f.write('\n'.join(command))
        _ = subprocess.check_output([PCETools.BLUEBEAM_ENGINE_DIR, "Script('set_markup.bci')"])
        os.remove("set_markup.bci")

    @staticmethod
    def set_replace(file_dir, i, before, after):
        markups = PCETools.return_markup_by_page(file_dir, i)
        markups = PCETools.get_markup_with_content(markups, before)
        markup_ids_dict = {k: {"comment": after} for k, _ in markups.items()}
        PCETools.set_markup(file_dir, i, markup_ids_dict)

    @staticmethod
    def paste_markup_to_file(standard_form, new_file, page_number=1, new_page_number=1, region=None, offset=(0, 0), content_replace_dict=None):
        logger.info("paste_markup_to_file for page {} Start.".format(page_number))
        markups = PCETools.return_markup_by_page(standard_form, page_number)
        if region is not None:
            markups = PCETools.get_markup_in_region(markups, region)
        if len(markups) == 0:
            logger.error("paste_markup_to_file for page {}: no markup.".format(page_number))
            return
        logger.info("return_markup_by_page for page {} finished.".format(page_number))
        fn = lambda value: (float(value['x']) + offset[0] if 'x' in value else None, float(value['y']) + offset[1] if 'y' in value else None, float(value['height']) if 'height' in value else None, value["comment"])
        content = list(zip(PCETools.copy_markup_batch(standard_form, page_number, markups), [fn(value) for _, value in markups.items()]))
        logger.info("copy_markup for page {} finished.".format(page_number))
        PCETools.paste_markup(new_file, new_page_number, content, content_replace_dict)

    @staticmethod
    def paste_all_markup_to_file_by_anchor(standard_form, new_file, anchor_color="#7A0000"):
        pages = PCETools.page_count(standard_form)
        assert pages == PCETools.page_count(new_file), "file page count mismatch"
        for i in range(1, pages + 1):
            markups_1, markups_2 = PCETools.return_markup_by_page(standard_form, i), PCETools.return_markup_by_page(new_file, i)
            markups_1, markups_2 = [markup for markup in markups_1.values() if markup["color"].lower() == anchor_color.lower()], [markup for markup in markups_2.values() if markup["color"].lower() == anchor_color.lower()]
            assert len(markups_1) > 0 and len(markups_2) > 0, "expected markup with the color {}, but found ({}, {})".format(anchor_color, len(markups_1), len(markups_2))
            markup_1, markup_2 = markups_1[0], markups_2[0]
            offset = (float(markup_2['x']) - float(markup_1['x']), float(markup_2['y']) - float(markup_1['y']))
            PCETools.paste_markup_to_file(standard_form, new_file, i, i, offset)

    @staticmethod
    def mix_patch(standard_form, file_list, output_path):
        markups = PCETools.return_markup_by_page(standard_form, 1)
        color_position = {item["color"].upper(): (float(item["x"]), float(item["y"])) for item in markups.values()}
        page_counts = [PCETools.page_count(f) for f in file_list]
        for i in range(max(page_counts)):
            et_list, coord_list = [], []
            for j in range(len(file_list)):
                if i >= page_counts[j]:
                    continue
                markup_list = list(PCETools.return_markup_by_page(file_list[j], i + 1).values())
                markup_item = [(markup["color"].upper(), (float(markup["x"]), float(markup["y"]))) for markup in markup_list if markup["color"].upper() in color_position]
                assert len(markup_item) == 1, f"Bad page in {file_list[j]}, page {i}: {markup_item}"
                markup_item = markup_item[0]
                coord_list.append((color_position[markup_item[0]][0] - markup_item[1][0], color_position[markup_item[0]][1] - markup_item[1][1]))
                et_list.append(PCETools.get_ET(file_list[j], i))
            standard_form_size = PCETools.page_size(standard_form, 0)
            PCETools.merge_page(et_list, coord_list, standard_form_size, os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.svg"))
            pdf_path = os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.pdf")
            PCETools.svg_to_pdf(os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.svg"), pdf_path)
            new_size = PCETools.page_size(pdf_path, 0)
            # TODO: This should be removed if svg_to_pdf is fixed well
            PCETools.resize_pdf(pdf_path, '100', new_size[0], new_size[1], 100 / standard_form_size[0] * new_size[0], standard_form_size[0], standard_form_size[1], pdf_path)
            PCETools.paste_markup_to_file(standard_form, pdf_path)
            if os.path.exists(os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.svg")):
                os.remove(os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.svg"))
        pdf_list = [os.path.join(PCETools.TEMP_PATH, f"{output_path}.{i}.pdf") for i in range(max(page_counts))]
        PCETools.combine_pdf(pdf_list, output_path)
        for f in pdf_list:
            if os.path.exists(f):
                os.remove(f)

    @staticmethod
    def pdf_color(page, page_number):
        svg_file = PCETools._get_svg_bytes_from_pdf(page, page_number)
        hex_color_pattern = re.compile(r'(#[A-Fa-f0-9]{6})')
        final_list =  hex_color_pattern.findall(svg_file)
        return set(final_list)

    @staticmethod
    def pdf_set_color(page, page_numbers, pre_color, post_color, output_path):
        page_count = PCETools.page_count(page)
        output_file = os.path.basename(output_path)
        svg_list = [os.path.join(PCETools.TEMP_PATH, f"{output_file}.{i}.svg") for i in range(page_count)]
        pdf_list = [os.path.join(PCETools.TEMP_PATH, f"{output_file}.{i}.pdf") for i in range(page_count)]
        for page_number in range(page_count):
            svg_file = PCETools._get_svg_bytes_from_pdf(page, page_number)
            if page_number in page_numbers:
                svg_file = svg_file.replace(pre_color.lower(), post_color).replace(pre_color.upper(), post_color)
            with open(svg_list[page_number], 'w') as f:
                f.write(svg_file)
            PCETools.svg_to_pdf(svg_list[page_number], pdf_list[page_number])
        PCETools.combine_pdf(pdf_list, output_path)
        for f in svg_list:
            os.remove(f)
        for f in pdf_list:
            os.remove(f)

    @staticmethod
    def pdf_color_v2(page, page_number):
        et = PCETools.get_ET(page, page_number)
        result = set()
        for elem in et.iter():
            if 'fill' in elem.attrib:
                if re.match(r'(#[A-Fa-f0-9]{6})', elem.attrib["fill"]):
                    result.add(elem.attrib["fill"])
            if 'stroke' in elem.attrib:
                if re.match(r'(#[A-Fa-f0-9]{6})', elem.attrib["stroke"]):
                    result.add(elem.attrib["stroke"])
        return result

    @staticmethod
    def pdf_set_color_v2(page, page_numbers, pre_color, post_color, output_path, opacity=1.0):
        page_count = PCETools.page_count(page)
        output_file = os.path.basename(output_path)
        svg_list = [os.path.join(PCETools.TEMP_PATH, f"{output_file}.{i}.svg") for i in range(page_count)]
        pdf_list = [os.path.join(PCETools.TEMP_PATH, f"{output_file}.{i}.pdf") for i in range(page_count)]
        for page_number in range(page_count):
            et = PCETools.get_ET(page, page_number)
            if page_number in page_numbers:
                for elem in et.iter():
                    if 'fill' in elem.attrib and (pre_color.lower() in elem.attrib["fill"] or pre_color.upper() in elem.attrib["fill"]):
                        elem.attrib["fill"] = elem.attrib["fill"].replace(pre_color.lower(), post_color).replace(pre_color.upper(), post_color)
                        if float(opacity) < 1.0:
                            elem.attrib["fill-opacity"] = str(opacity)
                    if 'stroke' in elem.attrib and (pre_color.lower() in elem.attrib["stroke"] or pre_color.upper() in elem.attrib["stroke"]):
                        elem.attrib["stroke"] = elem.attrib["stroke"].replace(pre_color.lower(), post_color).replace(pre_color.upper(), post_color)
                        if float(opacity) < 1.0:
                            elem.attrib["stroke-opacity"] = str(opacity)
            with open(svg_list[page_number], 'wb') as f:
                root = ET.ElementTree(et)
                root.write(f)
            PCETools.svg_to_pdf(svg_list[page_number], pdf_list[page_number])
        PCETools.combine_pdf(pdf_list, output_path)
        for f in svg_list:
            os.remove(f)
        for f in pdf_list:
            os.remove(f)

    @staticmethod
    def split_pdf(input_pdf, output_dir):
        with open(input_pdf, 'rb') as file:
            reader = pypdf.PdfReader(file)
            if len(reader.pages) == 1:
                output_list = [os.path.join(output_dir, '0.pdf')]
                shutil.copy(input_pdf, output_list[0])
                return output_list
            for i in range(len(reader.pages)):
                writer = pypdf.PdfWriter()
                writer.add_page(reader.pages[i])
                output_pdf = os.path.join(output_dir, '{}.pdf'.format(i))
                with open(output_pdf, 'wb') as output_file:
                    writer.write(output_file)
            return [os.path.join(output_dir, '{}.pdf'.format(i)) for i in range(len(reader.pages))]

    @staticmethod
    def pdf_content_move(input_file, output_file, offset, pages="all"):
        reader = pypdf.PdfReader(input_file)
        writer = pypdf.PdfWriter()
        page = reader.pages[0]
        offset_x, offset_y = offset
        for page_id in range(len(reader.pages)):
            if pages != 'all' and (type(pages) == 'list' and page_id not in pages):
                writer.add_page(page)
                continue
            assert page.rotation in [0, 90, 180, 270]
            if page.rotation == 0:
                op = pypdf.Transformation().translate(offset_x, offset_y)
            elif page.rotation == 90:
                op = pypdf.Transformation().translate(-offset_y, offset_x)
            elif page.rotation == 180:
                op = pypdf.Transformation().translate(-offset_x, -offset_y)
            else:
                op = pypdf.Transformation().translate(offset_y, -offset_x)
            page.add_transformation(op)
            writer.add_page(page)
        writer.write(output_file)
