import matlab.engine

from epowcore.simscape.config_manager import ConfigManager
from epowcore.simscape.port_handles import PortHandles
from epowcore.simscape.block import SimscapeBlock


def connect(
    eng: matlab.engine.MatlabEngine,
    sys_name: str,
    out_block: SimscapeBlock,
    out_ports: str | None,
    in_block: SimscapeBlock,
    in_ports: str | None,
) -> None:
    if out_ports is None:
        out_ports = ""
    if in_ports is None:
        in_ports = ""
    out_handles: PortHandles | None = get_port_handles(out_block, out_ports)
    in_handles: PortHandles | None = get_port_handles(in_block, in_ports)
    if out_handles is None or in_handles is None:
        raise ValueError(
            f"PortHandles for {out_block.type.name} or {in_block.type.name} are not defined!"
        )
    length = min(out_handles.length, in_handles.length)

    if out_handles.name == "Inport" or in_handles.name == "Outport":
        # Swap blocks
        out_block, in_block = in_block, out_block
        out_handles, in_handles = in_handles, out_handles

    mat_out_handles = _get_matlab_port_handles(eng, out_block, out_handles, length)
    mat_in_handles = _get_matlab_port_handles(eng, in_block, in_handles, length)

    try:
        eng.add_line(sys_name, mat_out_handles, mat_in_handles, "autorouting", "smart")
    except Exception as ex:
        raise ValueError(
            f"Failed to connect {out_block.name} to {in_block.name} in {sys_name}"
        ) from ex


def _get_matlab_port_handles(
    eng: matlab.engine.MatlabEngine,
    block: SimscapeBlock,
    handles: PortHandles,
    target_length: int | None = None,
) -> matlab.double | float:
    if target_length is None:
        target_length = handles.length

    all_handles = eng.get_param(block.name, "PortHandles")
    if not isinstance(all_handles, dict):
        raise ValueError("PortHandles Matlab call failed.")
    mat_handles = all_handles[handles.name]

    if isinstance(mat_handles, float):
        if handles.length > 1 or handles.start != 0:
            raise ValueError("Defined PortHandles don't match Matlab PortHandles!")
        if target_length > 1:
            raise ValueError("Requested PortHandle length can't be met!")
        return mat_handles
    elif mat_handles.size == (0, 0):  # not sure about this
        raise ValueError("Matlab PortHandles are empty!")

    mat_handles = mat_handles[0]
    end = handles.start + target_length
    return mat_handles[handles.start : end]


def get_port_handles(block: SimscapeBlock, port_name: str) -> PortHandles | None:
    """Tries to find the PortHandles for the given block type and port name.
    If the PortHandles are not defined, None is returned.

    :param block_type: The type of the block
    :param port_name: The name of the port at the block (empty string for first entry)
    :return: The PortHandles or None
    """
    if block.template is not None:
        template_handles = block.template.port_handles
        if port_name == "":
            return template_handles[0]

        for h in template_handles:
            if h.key == port_name:
                return h

    handle = ConfigManager.get_specific_porthandles(block.type, port_name)
    if handle is not None:
        return handle

    if port_name == "":
        handles = ConfigManager.get_all_porthandles(block.type)
        if handles is not None and handles:
            return handles[0]

    return None
