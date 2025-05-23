import lxml.etree as ET
import inkex


class SVGFile:
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    def __init__(self, file_name):
        self.file_name = file_name
        self.svg_xml = ET.parse(file_name)
        self.svg = self.svg_xml.getroot()

    def find_all(self, tag):
        return self.svg.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes(self, tag, attribute):
        elements = self.find_all(tag)
        return {element.attrib[attribute]: element for element in elements}

    def find_all_in_node(self, node, tag):
        return node.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, node, tag, attribute):
        elements = self.find_all_in_node(node, tag)
        return {element.attrib[attribute]: element for element in elements}

    def all_spans_in_text(self, text_node):
        return text_node.findall(".//tspan", namespaces=self.NAMESPACE_MAP)

    def write(self, file_name):
        self.svg_xml.write(file_name)


class SvgNode:
    NAMESPACE_MAP = {
        "html": "http://www.w3.org/1999/xhtml",
        "xlink": "http://www.w3.org/1999/xlink",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xmlns": "http://www.w3.org/2000/xmlns/",
        None: "http://www.w3.org/2000/svg",
    }

    def __init__(self, node):
        self.node = node

    def find_all_in_node(self, tag):
        return self.node.findall(".//{}".format(tag), namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, tag, attribute):
        elements = self.find_all_in_node(tag)
        return {element.attrib[attribute]: element for element in elements}


def render_svg_to_pdf(svg_path, pdf_path):
    """
    Converts an SVG file to a PDF using Inkex.

    :param svg_path: Path to the input SVG file.
    :param pdf_path: Path to the output PDF file.
    """
    if not inkex.command.is_inkscape_available():
        raise RuntimeError("Inkscape is not available. Please install it.")

    try:
        # Correctly pass arguments as separate strings
        inkex.command.inkscape(svg_path, "--export-filename", pdf_path)
    except Exception as e:
        raise RuntimeError(f"Failed to convert {svg_path} to PDF: {e}")
