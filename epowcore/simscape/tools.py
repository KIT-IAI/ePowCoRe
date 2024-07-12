import re
from typing import Any
import matlab.engine
from epowcore.generic.logger import Logger
from epowcore.simscape.block import SimscapeBlock


def set_position(
    eng: matlab.engine.MatlabEngine,
    block: SimscapeBlock,
    pos_x: int | float,
    pos_y: int | float,
) -> None:
    """Set the position of a Simulink block."""
    old_pos = matlab_array_to_list(eng.get_param(block.name, "Position"))

    eng.set_param(
        block.name,
        "Position",
        format_position(old_pos, int(pos_x), int(pos_y)),
        nargout=0,
    )


def get_position(eng: matlab.engine.MatlabEngine, block: SimscapeBlock) -> tuple[float, ...]:
    """Get the position of a Simulink block."""
    return tuple(matlab_array_to_list(eng.get_param(block.name, "Position")))


def format_position(pos_array: list[float], pos_x: int, pos_y: int) -> str:
    """Create a valid position string for Simulink blocks.

    :param pos_array: A list containing x_start, y_start, x_end, y_end.
    :type pos_array: list[float]
    :param pos_x: The new x position.
    :type pos_x: int
    :param pos_y: The new y position.
    :type pos_y: int
    :return: A position string with the new x-y-position and old size.
    :rtype: str
    """
    size_x = pos_array[2] - pos_array[0]
    size_y = pos_array[3] - pos_array[1]
    return f"[{int(pos_x)} {int(pos_y)} {int(pos_x + size_x)} {int(pos_y + size_y)}]"


def matlab_array_to_list(matlab_array: Any) -> list[float]:
    """Convert a Matlab array to a Python list."""
    if not isinstance(matlab_array, (list, matlab.double)):
        raise TypeError(f"Expected list, got {type(matlab_array)}")
    return [float(x) for x in matlab_array[0]]


def sanitize_tag_name(name: str, max_length: int = 63) -> str:
    """Valid identifiers start with a letter, contain no spaces or special characters
    and are at most 63 characters long."""
    # manually convert - to _ (just for better recognition)
    sname = name.replace("-", "_")
    sname = re.sub(r"[^a-zA-Z0-9_]", "", name)
    if len(sname) > max_length:
        return sname[:max_length]

    return sname


def flip_block_left_right(eng: matlab.engine.MatlabEngine, block: SimscapeBlock) -> None:
    """Flip a block left or right."""
    if eng.get_param(block.name, "Orientation") == "left":
        eng.set_param(block.name, "Orientation", "right", nargout=0)
    else:
        eng.set_param(block.name, "Orientation", "left", nargout=0)


def get_param_in_bounds(
    value: float,
    lower_bound: float,
    upper_bound: float,
    param_desc: str | None = None,
    log: bool = True,
) -> float:
    """Check if the given parameter is in the given boundaries.
    Return the closer boundary if not, and log this instance by default.

    :param value: The parameter value to check.
    :type value: float
    :param lower_bound: The lower bound.
    :type lower_bound: float
    :param upper_bound: The upper bound.
    :type upper_bound: float
    :param param_desc: The description of the parameter (block + parameter name), defaults to None
    :type param_desc: str | None, optional
    :param log: Whether to log the out of bounds instance, defaults to True
    :type log: bool, optional
    :return: The value inside the boundaries.
    :rtype: float
    """
    assert not log or param_desc

    if value < lower_bound:
        if log:
            Logger.log_to_selected(
                f"Value below lower bound. {param_desc}: {value} -> {lower_bound}"
            )
        return lower_bound
    if value > upper_bound:
        if log:
            Logger.log_to_selected(
                f"Value over upper bound. {param_desc}: {value} -> {upper_bound}"
            )
        return upper_bound
    return value
