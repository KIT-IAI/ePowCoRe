from enum import Enum
from typing import NamedTuple

from epowcore.simscape.shared import SimscapeBlockType
from epowcore.simscape.templates.base_template import SubsystemTemplate


class SimscapeBlock(NamedTuple):
    """A description of a Simscape block consisting of the name and the block type."""

    name: str
    type: SimscapeBlockType
    template: SubsystemTemplate | None = None
