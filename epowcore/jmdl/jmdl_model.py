from enum import Enum
import re
from typing import Any
from dataclasses import dataclass, field
import json


from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger


class DataType(Enum):
    """Data types for JMDL"""

    FLOAT64 = "float64"
    INT64 = "int64"
    STRING = "string"
    GROUP = "group"
    ENUM = "enum"
    BOOL = "bool"
    IMAGE = "image"


@dataclass
class Data:
    """Data class for JMDLImport"""

    description: str = field(default="")
    data_type: DataType = field(default=DataType.FLOAT64)
    entries: list["Data"] = field(default_factory=list)
    value: Any = field(default=None)
    enum_class: str | None = field(default=None)
    name: str = field(default="")

    def get_content(self) -> Any:
        """Get the content of the data"""
        if self.data_type == DataType.GROUP:
            return self.entries
        return self.value

    @property
    def entries_dict(self) -> dict:
        """Get the entries dict"""
        entries_out: dict = {}
        for entry in self.entries:
            entries_out = entries_out | {entry.name: entry}
        return entries_out

    def as_dict(self) -> dict:
        """Get the dict of the data"""
        if self.data_type == DataType.GROUP:
            entries_out: dict = {}
            for entry in self.entries:
                entries_out = entries_out | entry.as_dict()
            return {
                self.name: {
                    "description": self.description,
                    "type": self.data_type.value,
                    "entries": entries_out,
                }
            }
        if self.data_type == DataType.ENUM:
            return {
                self.name: {
                    "description": self.description,
                    "type": self.data_type.value,
                    "value": self.value,
                    "enumClass": self.enum_class,
                }
            }
        if self.data_type == DataType.IMAGE:
            return {
                self.name: {
                    "description": self.description,
                    "type": self.data_type.value,
                    "filename": self.value,
                }
            }
        return {
            self.name: {
                "description": self.description,
                "type": self.data_type.value,
                "value": self.value,
            }
        }

    @staticmethod
    def from_dict(obj: dict, _name: str) -> "Data":
        """Create a Data object from a dict"""
        if not all(key in obj for key in ["description", "type"]):
            raise ValueError(
                "The dictionary to create a data object from must have a description and a type entry."
            )
        _decription = str(obj.get("description"))
        _dataType = DataType(obj.get("type"))

        _entries: list[Data] = []
        _value = None
        _enumClass = None
        if _dataType == DataType.GROUP:
            entries = obj.get("entries")
            if isinstance(entries, dict):
                _entries = [Data.from_dict(entry, name) for name, entry in entries.items()]
        elif _dataType == DataType.IMAGE:
            _value = obj.get("filename")
        elif _dataType == DataType.ENUM:
            _value = obj.get("value")
            _enumClass = obj.get("enumClass")
        else:
            _value = obj.get("value")
        return Data(_decription, _dataType, _entries, _value, _enumClass, _name)


@dataclass
class Layout:
    """Layout class for JMDLImport"""

    center: list[float] = field(default_factory=lambda: [0.0, 0.0])
    size: list[float] = field(default_factory=lambda: [10.0, 10.0])
    backgroundColor: str = field(default_factory=lambda: "#d3d3d3ff")
    borderColor: str = field(default_factory=lambda: "#000000ff")
    borderThickness: str = field(default_factory=lambda: "5.0%")
    radiusNW: str = field(default_factory=lambda: "0.0px")
    radiusNE: str = field(default_factory=lambda: "0.0px")
    radiusSW: str = field(default_factory=lambda: "0.0px")
    radiusSE: str = field(default_factory=lambda: "0.0px")

    def as_dict(self) -> dict:
        """Get the dict of the layout"""
        return {
            "center": self.center,
            "size": self.size,
            "backgroundColor": self.backgroundColor,
            "borderColor": self.borderColor,
            "borderThickness": self.borderThickness,
            "radiusNW": self.radiusNW,
            "radiusNE": self.radiusNE,
            "radiusSW": self.radiusSW,
            "radiusSE": self.radiusSE,
        }

    @staticmethod
    def from_dict(obj: dict) -> "Layout":
        """Create a Layout object from a dict"""
        _center = obj.get("center", [0, 0])
        assert _center is None or len(_center) == 2
        _size = obj.get("size", [10, 10])
        assert _size is None or len(_size) == 2
        _backgroundColor = obj.get("backgroundColor", "#d3d3d3ff")
        _borderColor = obj.get("borderColor", "#000000ff")
        _borderThickness = obj.get("borderThickness", "5.0%")
        _radiusNW = obj.get("radiusNW", "0.0px")
        _radiusNE = obj.get("radiusNE", "0.0px")
        _radiusSW = obj.get("radiusSW", "0.0px")
        _radiusSE = obj.get("radiusSE", "0.0px")
        return Layout(
            _center,
            _size,
            _backgroundColor,
            _borderColor,
            _borderThickness,
            _radiusNW,
            _radiusNE,
            _radiusSW,
            _radiusSE,
        )


@dataclass
class CableLayout:
    """Layout with a diameter for cables"""

    borderPos: float = field(default=Configuration().get("JMDL.Import.Cable.borderPos"))
    diameter: str = field(default=Configuration().get("JMDL.Import.Cable.diameter"))
    color: str = field(default=Configuration().get("JMDL.Import.Cable.color"))

    def as_dict(self) -> dict:
        """Get the dict of the layout"""
        return {
            "borderPos": self.borderPos,
            "diameter": self.diameter,
            "color": self.color,
        }

    @staticmethod
    def from_dict(obj: dict) -> "CableLayout":
        """Create a LayoutSmall object from a dict"""
        _borderPos = float(obj.get("borderPos", 0.0))
        _diameter = obj.get("diameter", "7.0%")
        _color = obj.get("color", "#000000ff")
        return CableLayout(_borderPos, _diameter, _color)


@dataclass
class BorderLayout:
    """Another Layout variant"""

    thickness: int = field(default=1)
    color: str = field(default="#000000ff")
    points: list[float] = field(default_factory=list)
    geo_points: list[float] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Get the dict of the layout"""
        return {
            "thickness": self.thickness,
            "color": self.color,
            "points": self.points,
            "geoPoints": self.geo_points,
        }

    @staticmethod
    def from_dict(obj: dict) -> "BorderLayout":
        """Create a Layout3 object from a dict"""
        _thickness = int(obj.get("thickness", 1))
        _color = obj.get("color", "#000000ff")
        _points = obj.get("points", [])
        _geo_points = obj.get("geoPoints", [])
        return BorderLayout(_thickness, _color, _points, _geo_points)


@dataclass
class PortInternals:
    """The positioning of a block within a super block"""

    x: float = field(default=0.0)
    y: float = field(default=0.0)
    diameter: float = field(default=20.0)
    color: str = field(default="#000000ff")

    def as_dict(self) -> dict:
        """Get the dict of the layout"""
        return {
            "x": self.x,
            "y": self.y,
            "diameter": self.diameter,
            "color": self.color,
        }

    @staticmethod
    def from_dict(obj: dict) -> "PortInternals":
        """Create a PortInternals object from a dict"""
        _x = obj.get("x", 0.0)
        _y = obj.get("y", 0.0)
        _diameter = obj.get("diameter", 20.0)
        _color = obj.get("color", "#000000ff")
        return PortInternals(_x, _y, _diameter, _color)


@dataclass
class Port:
    """Port class for JMDLImport"""

    type: str
    name: str
    layout: CableLayout
    internal: PortInternals | None = field(default=None)

    def as_dict(self) -> dict:
        """Get the dictionary representation of the port"""
        internal = (
            {"internal": {"layout": self.internal.as_dict()}} if self.internal is not None else {}
        )
        return {self.name: ({"type": self.type, "layout": self.layout.as_dict()} | internal)}

    @staticmethod
    def from_dict(obj: dict, name: str) -> "Port":
        """Create a Port object from a dict"""
        _type = obj.get("type", "")
        _layout = CableLayout.from_dict(obj.get("layout", {}))
        _internal = (
            PortInternals.from_dict(obj.get("internal", {}).get("layout", {}))
            if obj.get("internal", {}).get("layout", {})
            else None
        )
        return Port(_type, name, _layout, _internal)


@dataclass
class Connection:
    """Connection class for JMDLImport"""

    start: str
    end: str
    layout: BorderLayout

    def as_dict(self) -> dict:
        """Get the dict of the connection"""
        return {
            "start": self.start,
            "end": self.end,
            "layout": self.layout.as_dict(),
        }

    @staticmethod
    def from_dict(obj: dict) -> "Connection":
        """Create a Connection object from a dict"""
        _start = obj.get("start", "")
        _end = obj.get("end", "")
        _layout = BorderLayout.from_dict(obj.get("layout", {}))
        return Connection(_start, _end, _layout)


@dataclass(unsafe_hash=True)
class Block:
    """Block class for JMDLImport"""

    name: str
    ports: list[Port]
    block_type: str
    block_class: str = field(default="")
    comment: str = field(default="")
    url: str = field(default="")
    tags: list[str] = field(default_factory=list)
    data: Data = field(default_factory=Data)
    layout: CableLayout | Layout = field(default_factory=Layout)

    def as_dict(self) -> dict:
        ports: dict = {}
        for port in self.ports:
            ports = ports | port.as_dict()
        return {
            self.name: {
                "ports": ports,
                "type": self.block_type,
                "class": self.block_class,
                "comment": self.comment,
                "url": self.url,
                "tags": self.tags,
                "layout": self.layout.as_dict(),
            }
            | self.data.as_dict(),
        }

    @staticmethod
    def from_dict(obj: dict, _name: str) -> "Block":
        """Create a Block object from a dict"""
        _ports = [Port.from_dict(port, name) for name, port in obj.get("ports", {}).items()]
        _type = obj.get("type", "")
        _class = obj.get("class", "")
        _comment = obj.get("comment", "")
        _url = obj.get("url", "")
        _tags = list(obj.get("tags", []))
        _data = Data.from_dict(obj.get("data", {}), "data")
        _layout: Layout | CableLayout = (
            CableLayout.from_dict(obj.get("layout", {}))
            if obj.get("layout", {}).get("borderPos") is not None
            else Layout()
        )
        _layout = (
            Layout.from_dict(obj.get("layout", {}))
            if obj.get("layout", {}).get("center") is not None
            else _layout
        )
        return Block(
            _name,
            _ports,
            _type,
            _class,
            _comment,
            _url,
            _tags,
            _data,
            _layout,
        )


@dataclass
class Root:
    """Root class for JMDLImport"""

    name: str
    ports: list[Port]
    _type: str
    blocks: list[Block]
    super_blocks: "list[Root]"
    connections: list[Connection]
    comment: str
    url: str
    tags: list[str]
    data: Data
    layout: Layout

    def as_dict(self) -> dict:
        """Convert the object to a dict"""
        blocks: dict = {}
        for block in self.blocks:
            blocks = blocks | block.as_dict()
        for root in self.super_blocks:
            blocks = blocks | root.as_dict()
        ports: dict = {}
        for port in self.ports:
            ports = ports | port.as_dict()
        return {
            self.name: {
                "ports": ports,
                "type": self._type,
                "blocks": blocks,
                "connections": [connection.as_dict() for connection in self.connections],
                "comment": self.comment,
                "url": self.url,
                "tags": self.tags,
                "layout": self.layout.as_dict(),
            }
            | self.data.as_dict(),
        }

    @staticmethod
    def from_dict(obj: dict, name: str) -> "Root":
        """Create a Root object from a dict"""
        if isinstance(obj, dict):
            _ports = [Port.from_dict(port, name) for name, port in obj.get("ports", {}).items()]
            _type = obj.get("type", "")
            _blocks = [
                Block.from_dict(block, name)
                for name, block in obj.get("blocks", {}).items()
                if "class" in block.keys()
            ]
            _super_blocks = [
                Root.from_dict(block, name)
                for name, block in obj.get("blocks", {}).items()
                if not "class" in block.keys()
            ]
            _connections = [
                Connection.from_dict(connection) for connection in obj.get("connections", [])
            ]
            _comment = obj.get("comment", "")
            _url = obj.get("url", "")
            _tags = [tag for tag in obj.get("tags", [])]
            _data = Data.from_dict(obj.get("data", {}), "data")

        _layout = Layout.from_dict(obj.get("layout", {}))
        return Root(
            name,
            _ports,
            _type,
            _blocks,
            _super_blocks,
            _connections,
            _comment,
            _url,
            _tags,
            _data,
            _layout,
        )


@dataclass
class Tag:
    """Tag class for JMDLImport"""

    label: str
    color: str

    def as_dict(self) -> dict:
        """Convert the object to a dict"""
        return {"label": self.label, "color": self.color}

    @staticmethod
    def from_dict(obj: dict) -> "Tag":
        """Create a Tag object from a dict"""
        _label = obj.get("label")
        _color = obj.get("color")
        if _color is None or _label is None:
            raise ValueError(
                "The dictionary to create a tag from must have a label and a color entry."
            )

        # Assert color is valid
        color_reg = re.compile(r"#[0-9a-fA-F]{6}")
        if _color:
            assert color_reg.match(_color)

        return Tag(_label, _color)


@dataclass
class JmdlModel:
    """Class to import JMDL files"""

    version: str
    geo_mode: bool
    data: Data
    root: Root
    tag_database: list[Tag]

    def as_dict(self) -> dict:
        """Convert the object to a dict"""
        return {
            "version": self.version,
            "geoMode": self.geo_mode,
            "/": self.root.as_dict()["/"],
            "tagDatabase": [tag.as_dict() for tag in self.tag_database],
        } | self.data.as_dict()

    def to_json(self, minified: bool = False) -> str:
        """Convert the object to a JSON string"""
        if minified:
            return json.dumps(self.as_dict(), separators=(",", ":"))
        return json.dumps(self.as_dict(), indent=4)

    @property
    def base_frequency(self) -> float:
        """Get the base frequency of the model"""
        if "frequency" not in self.data.entries_dict.keys():
            default = Configuration().get_default("JmdlModel", "base_frequency", Platform.JMDL)
            if default is None:
                raise ValueError("Could not find default value for JmdlModel.base_frequency")
            Logger.log_to_selected(
                f"Using default for {type(self).__name__}: base_frequency = {default}"
            )
            return default
        return self.data.entries_dict["frequency"].value

    @property
    def base_mva(self) -> float:
        """Get the base frequency of the model"""
        if "baseMVA" not in self.data.entries_dict.keys():
            default = Configuration().get_default("JmdlModel", "base_mva", Platform.JMDL)
            if default is None:
                raise ValueError("Could not find default value for JmdlModel.base_mva")
            Logger.log_to_selected(f"Using default for {type(self).__name__}: base_mva = {default}")
            return default
        return self.data.entries_dict["baseMVA"].value

    @staticmethod
    def from_dict(obj: dict) -> "JmdlModel":
        """Create a JMDLImport object from a dictionary"""
        _version = str(obj.get("version"))
        _geo_mode = bool(obj.get("geoMode"))
        _data = Data.from_dict(obj.get("data", {}), "data")
        _root = Root.from_dict(obj.get("/", {}), "/")
        _tag_database = [Tag.from_dict(tag) for tag in obj.get("tagDatabase", [])]
        return JmdlModel(_version, _geo_mode, _data, _root, _tag_database)
