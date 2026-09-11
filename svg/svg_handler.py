import os
from pathlib import Path
from typing import Optional

import lxml.etree as ET
import inkex

# Single shared namespace map, imported by all SVG modules (Q6)
NAMESPACE_MAP = {
    "html": "http://www.w3.org/1999/xhtml",
    "xlink": "http://www.w3.org/1999/xlink",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xmlns": "http://www.w3.org/2000/xmlns/",
    None: "http://www.w3.org/2000/svg",
}


class Template:
    """Generic SVG template that can be loaded from a file."""

    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(self, path: Optional[str] = None):
        self.template_path = Path(path) if path else None
        if self.template_path:
            self.svg_xml = ET.parse(self.template_path)
            self.svg = self.svg_xml.getroot()

    def get_element_by_id(self, element_id: str) -> Optional[ET.Element]:
        """Get first element matching the given id attribute."""
        results = self.svg.findall(f".//*[@id='{element_id}']")
        return results[0] if results else None

    def find_all_by_tag(self, tag: str, parent: Optional[ET.Element] = None) -> list[ET.Element]:
        """Find all descendant elements with the given local tag name."""
        root = parent if parent is not None else self.svg
        return root.findall(".//" + tag, namespaces=self.NAMESPACE_MAP)

    def find_by_tag_and_attribute(
        self,
        parent: ET.Element,
        tag: str,
        attribute: str,
    ) -> Optional[ET.Element]:
        """Return first child element with matching tag that has the given attribute."""
        for elem in parent.findall(".//" + tag, namespaces=self.NAMESPACE_MAP):
            if attribute in elem.attrib:
                return elem
        return None

    def write(self, path: str) -> None:
        """Write template to file."""
        self.svg_xml.write(path)


class SVGFile:
    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(self, file_name):
        self.file_name = file_name
        self.svg_xml = ET.parse(file_name)
        self.svg = self.svg_xml.getroot()

    def find_all(self, tag):
        return self.svg.findall(".//" + tag, namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes(self, tag, attribute):
        elements = self.find_all(tag)
        return {
            element.attrib[attribute]: element
            for element in elements
            if attribute in element.attrib
        }

    def find_all_in_node(self, node, tag):
        return node.findall(".//" + tag, namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, node, tag, attribute):
        elements = self.find_all_in_node(node, tag)
        return {
            element.attrib[attribute]: element
            for element in elements
            if attribute in element.attrib
        }

    def all_spans_in_text(self, text_node):
        return text_node.findall(".//tspan", namespaces=self.NAMESPACE_MAP)

    def write(self, file_name):
        self.svg_xml.write(file_name)


class SvgNode:
    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(self, node):
        self.node = node

    def find_all_in_node(self, tag):
        return self.node.findall(".//" + tag, namespaces=self.NAMESPACE_MAP)

    def find_all_elements_by_attributes_in_node(self, tag, attribute):
        elements = self.find_all_in_node(tag)
        return {
            element.attrib[attribute]: element
            for element in elements
            if attribute in element.attrib
        }


def _ensure_inkscape():
    """Ensure Inkscape executable is discoverable by inkex."""
    if not inkex.command.is_inkscape_available():
        candidate_dirs = [
            "/Applications/Inkscape.app/Contents/MacOS",
            "/opt/homebrew/bin",
            "/usr/local/bin",
            os.path.expanduser("~/.local/bin"),
        ]
        for candidate_dir in candidate_dirs:
            candidate_bin = os.path.join(candidate_dir, "inkscape")
            if os.path.isfile(candidate_bin) and os.access(candidate_bin, os.X_OK):
                os.environ["PATH"] = f"{candidate_dir}:{os.environ.get('PATH', '')}"
                break


def render_svg_to_pdf(svg_path, pdf_path):
    """
    Converts an SVG file to a PDF using Inkex.

    :param svg_path: Path to the input SVG file.
    :param pdf_path: Path to the output PDF file.
    """
    _ensure_inkscape()
    if not inkex.command.is_inkscape_available():
        raise RuntimeError("Inkscape is not available. Please install it.")

    try:
        # Correctly pass arguments as separate strings
        inkex.command.inkscape(svg_path, "--export-filename", pdf_path)
    except Exception as e:
        raise RuntimeError(f"Failed to convert {svg_path} to PDF: {e}")
