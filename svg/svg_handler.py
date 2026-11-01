import copy
import os
from pathlib import Path
from typing import Any, Optional, Union

import inkex
import lxml.etree as ET

# Single shared namespace map, imported by all SVG modules (Q6)
NAMESPACE_MAP = {
    "html": "http://www.w3.org/1999/xhtml",
    "xlink": "http://www.w3.org/1999/xlink",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xmlns": "http://www.w3.org/2000/xmlns/",
    None: "http://www.w3.org/2000/svg",
}


class SvgElement:
    """
    Encapsulates an SVG XML element, completely wrapping lxml.etree._Element.
    Provides a clean, Pythonic API for DOM manipulation, creation, and querying.
    """

    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(
        self,
        element_or_tag: Union[str, ET._Element, "SvgElement"],
        attrib: Optional[dict[str, Any]] = None,
        text: Optional[str] = None,
    ):
        if isinstance(element_or_tag, str):
            str_attrib = {k: str(v) for k, v in attrib.items()} if attrib else {}
            self._element = ET.Element(element_or_tag, attrib=str_attrib)
            if text is not None:
                self._element.text = str(text)
        elif isinstance(element_or_tag, SvgElement):
            self._element = element_or_tag._element
            if attrib:
                for k, v in attrib.items():
                    self._element.attrib[k] = str(v)
            if text is not None:
                self._element.text = str(text)
        elif isinstance(element_or_tag, ET._Element):
            self._element = element_or_tag
            if attrib:
                for k, v in attrib.items():
                    self._element.attrib[k] = str(v)
            if text is not None:
                self._element.text = str(text)
        else:
            raise TypeError(f"Unsupported element type: {type(element_or_tag)}")

    @property
    def tag(self) -> str:
        """Local tag name without XML namespace."""
        t = self._element.tag
        return t.split("}")[-1] if "}" in t else t

    @property
    def attrib(self) -> dict[str, str]:
        """Access underlying attributes dictionary."""
        return self._element.attrib

    @property
    def text(self) -> Optional[str]:
        return self._element.text

    @text.setter
    def text(self, value: Optional[str]) -> None:
        self._element.text = str(value) if value is not None else None

    @property
    def tail(self) -> Optional[str]:
        return self._element.tail

    @tail.setter
    def tail(self, value: Optional[str]) -> None:
        self._element.tail = str(value) if value is not None else None

    @property
    def id(self) -> Optional[str]:
        return self._element.attrib.get("id")

    @id.setter
    def id(self, value: str) -> None:
        self._element.attrib["id"] = str(value)

    @property
    def raw_element(self) -> ET._Element:
        """Underlying lxml._Element for internal SVG rendering."""
        return self._element

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._element.attrib.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._element.attrib[key] = str(value)

    def __getitem__(self, key: Union[str, int]) -> Union[str, "SvgElement"]:
        if isinstance(key, int):
            return SvgElement(self._element[key])
        return self._element.attrib[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._element.attrib[key] = str(value)

    def __contains__(self, key: str) -> bool:
        return key in self._element.attrib

    def __len__(self) -> int:
        return len(self._element)

    def __iter__(self):
        for child in self._element:
            yield SvgElement(child)

    def iterchildren(self):
        for child in self._element.iterchildren():
            yield SvgElement(child)

    def create_child(
        self,
        tag: str,
        attrib: Optional[dict[str, Any]] = None,
        text: Optional[str] = None,
    ) -> "SvgElement":
        """Creates and appends a new child SvgElement."""
        str_attrib = {k: str(v) for k, v in attrib.items()} if attrib else {}
        child_elem = ET.SubElement(self._element, tag, attrib=str_attrib)
        if text is not None:
            child_elem.text = str(text)
        return SvgElement(child_elem)

    def append(self, child: Union["SvgElement", ET._Element]) -> None:
        """Appends a child SvgElement or raw Element."""
        raw = child._element if isinstance(child, SvgElement) else child
        self._element.append(raw)

    def remove(self, child: Union["SvgElement", ET._Element]) -> None:
        raw = child._element if isinstance(child, SvgElement) else child
        self._element.remove(raw)

    def find_by_id(self, element_id: str) -> Optional["SvgElement"]:
        """Finds first descendant element matching the given id attribute."""
        results = self._element.xpath(f".//*[@id='{element_id}']")
        return SvgElement(results[0]) if results else None

    def find_all(self, tag: str) -> list["SvgElement"]:
        """Finds all descendant elements matching the given local tag name or XPath expression."""
        if "[" in tag or "/" in tag or "@" in tag:
            path = tag if tag.startswith(".") else f".//{tag}"
            return self.findall(path)
        results = self._element.xpath(f".//*[local-name()='{tag}']")
        return [SvgElement(e) for e in results]

    def findall(self, path: str, namespaces: Optional[dict] = None) -> list["SvgElement"]:
        """Finds all elements matching the XPath pattern."""
        if namespaces is not None:
            return [SvgElement(e) for e in self._element.findall(path, namespaces=namespaces)]
        # Try with default namespace map first
        res = self._element.findall(path, namespaces=self.NAMESPACE_MAP)
        if not res:
            res = self._element.findall(path)
        return [SvgElement(e) for e in res]

    def find(self, path: str, namespaces: Optional[dict] = None) -> Optional["SvgElement"]:
        """Finds first element matching the XPath pattern."""
        res = self.findall(path, namespaces=namespaces)
        return res[0] if res else None

    def find_first(self, tag: str) -> Optional["SvgElement"]:
        elements = self.find_all(tag)
        return elements[0] if elements else None

    def find_all_with_attr(self, tag: str, attribute: str) -> dict[str, "SvgElement"]:
        """Returns {attr_val: SvgElement} for all matching descendants that have `attribute`."""
        elements = self.find_all(tag)
        return {
            elem.attrib[attribute]: elem
            for elem in elements
            if attribute in elem.attrib
        }

    def clone(self) -> "SvgElement":
        """Returns an independent deep copy of this element and its subtree."""
        return SvgElement(copy.deepcopy(self._element))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._element, name)


class SvgDocument:
    """
    Encapsulates an SVG document, providing parsing, cloning, querying, and serialization.
    """

    def __init__(
        self, tree_or_root: Union[ET._ElementTree, ET._Element, SvgElement]
    ):
        if isinstance(tree_or_root, ET._ElementTree):
            self._tree = tree_or_root
            self._root = SvgElement(self._tree.getroot())
        elif isinstance(tree_or_root, SvgElement):
            self._root = tree_or_root
            self._tree = ET.ElementTree(self._root.raw_element)
        elif isinstance(tree_or_root, ET._Element):
            self._root = SvgElement(tree_or_root)
            self._tree = ET.ElementTree(tree_or_root)
        else:
            raise TypeError(f"Unsupported document root: {type(tree_or_root)}")

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "SvgDocument":
        tree = ET.parse(str(path))
        return cls(tree)

    @classmethod
    def from_string(cls, xml_text: str) -> "SvgDocument":
        data = (
            xml_text.encode("utf-8")
            if isinstance(xml_text, str)
            else xml_text
        )
        root = ET.fromstring(data)
        return cls(root)

    @property
    def root(self) -> SvgElement:
        return self._root

    def find_by_id(self, element_id: str) -> Optional[SvgElement]:
        return self._root.find_by_id(element_id)

    def find_all(self, tag: str) -> list[SvgElement]:
        return self._root.find_all(tag)

    def findall(self, path: str, namespaces: Optional[dict] = None) -> list[SvgElement]:
        return self._root.findall(path, namespaces=namespaces)

    def find(self, path: str, namespaces: Optional[dict] = None) -> Optional[SvgElement]:
        return self._root.find(path, namespaces=namespaces)

    def find_all_with_attr(self, tag: str, attribute: str) -> dict[str, SvgElement]:
        return self._root.find_all_with_attr(tag, attribute)

    def clone(self) -> "SvgDocument":
        return SvgDocument(copy.deepcopy(self._tree))

    def write(self, path: Union[str, Path]) -> None:
        self._tree.write(str(path))

    def to_string(self, pretty_print: bool = True) -> str:
        return ET.tostring(
            self._tree, encoding="utf-8", pretty_print=pretty_print
        ).decode("utf-8")


class Template(SvgDocument):
    """Alias for SvgDocument for generic SVG template loading."""

    def __init__(self, path: Optional[Union[str, Path]] = None):
        if path:
            doc = SvgDocument.from_file(path)
            super().__init__(doc._tree)
        else:
            root = SvgElement("svg")
            super().__init__(root)

    def get_element_by_id(self, element_id: str) -> Optional[SvgElement]:
        return self.find_by_id(element_id)

    def find_all_by_tag(
        self, tag: str, parent: Optional[Union[SvgElement, ET._Element]] = None
    ) -> list[SvgElement]:
        if parent is not None:
            elem = parent if isinstance(parent, SvgElement) else SvgElement(parent)
            return elem.find_all(tag)
        return self.find_all(tag)

    def find_by_tag_and_attribute(
        self,
        parent: Union[SvgElement, ET._Element],
        tag: str,
        attribute: str,
    ) -> Optional[SvgElement]:
        elem = parent if isinstance(parent, SvgElement) else SvgElement(parent)
        for child in elem.find_all(tag):
            if attribute in child.attrib:
                return child
        return None


class SVGFile:
    """Legacy adapter for SVGFile over SvgDocument."""

    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(self, file_name):
        self.file_name = file_name
        self.doc = SvgDocument.from_file(file_name)
        self.svg_xml = self.doc._tree
        self.svg = self.doc.root

    def find_all(self, tag):
        return self.doc.find_all(tag)

    def find_all_elements_by_attributes(self, tag, attribute):
        return self.doc.find_all_with_attr(tag, attribute)

    def find_all_in_node(self, node, tag):
        elem = node if isinstance(node, SvgElement) else SvgElement(node)
        return elem.find_all(tag)

    def find_all_elements_by_attributes_in_node(self, node, tag, attribute):
        elem = node if isinstance(node, SvgElement) else SvgElement(node)
        return elem.find_all_with_attr(tag, attribute)

    def all_spans_in_text(self, text_node):
        elem = text_node if isinstance(text_node, SvgElement) else SvgElement(text_node)
        return elem.find_all("tspan")

    def write(self, file_name):
        self.doc.write(file_name)


class SvgNode:
    """Legacy adapter for SvgNode over SvgElement."""

    NAMESPACE_MAP = NAMESPACE_MAP

    def __init__(self, node):
        self._elem = node if isinstance(node, SvgElement) else SvgElement(node)
        self.node = self._elem.raw_element

    def find_all_in_node(self, tag):
        return self._elem.find_all(tag)

    def find_all_elements_by_attributes_in_node(self, tag, attribute):
        return self._elem.find_all_with_attr(tag, attribute)


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
        inkex.command.inkscape(str(svg_path), "--export-filename", str(pdf_path))
    except Exception as e:
        raise RuntimeError(f"Failed to convert {svg_path} to PDF: {e}")
