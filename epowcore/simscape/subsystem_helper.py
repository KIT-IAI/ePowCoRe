import os
import random
import string
import time

import matlab.engine
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.gdf.governors.gast import GAST
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A
from epowcore.simscape.block import SimscapeBlock
from epowcore.simscape.components.gast import set_parameters_gast
from epowcore.simscape.components.hygov import set_parameters_hygov
from epowcore.simscape.components.ieee_g1 import set_parameters_ieeeg1
from epowcore.simscape.components.ieee_pss1a import set_parameters_ieee_pss1a
from epowcore.simscape.components.ieee_pss2a import set_parameters_ieee_pss2a
from epowcore.simscape.components.ieee_st1a import set_parameters_ieee_st1a
from epowcore.simscape.components.sexs import set_parameters_sexs
import epowcore.simscape.simscape_converter

from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.subsystem import Subsystem
from epowcore.simscape.shared import SimscapeBlockType
from epowcore.simscape.templates.base_template import SubsystemTemplate
from epowcore.simscape.templates.generator_controls import GeneratorControlsTemplate

AVAILABLE_TEMPLATES = [
    GeneratorControlsTemplate(),
]


def get_subsystem_template(subsystem: Subsystem) -> SubsystemTemplate | None:
    """Find and return a matching template for the given subsystem.

    :param subsystem: The subsystem to check for a matching template.
    :type subsystem: Subsystem
    :return: The first matching template or None.
    :rtype: SubsystemTemplate | None
    """
    for template in AVAILABLE_TEMPLATES:
        if template.check_match(subsystem):
            return template

    return None


def insert_subsystem_template(
    eng: matlab.engine.MatlabEngine,
    model_name: str,
    subsystem: Subsystem,
    template: SubsystemTemplate,
    template_path: str = "./epowcore/simscape/templates",
) -> SimscapeBlock | None:
    """Loads a subsystem template and inserts it into the model."""
    block_list = eng.getfullname(eng.Simulink.findBlocks(model_name))
    if not isinstance(block_list, (list, str)):
        raise ValueError("Failed to get blocks.")
    if isinstance(block_list, str):
        block_list = [block_list]

    template_file_name: str = template.template_file_name
    subsystem_full_name = f"{model_name}/{subsystem.name}"

    # prevent name collisions
    if subsystem_full_name in block_list:
        subsystem_full_name = next(
            (
                f"{model_name}/{subsystem.name}_{i}"
                for i in range(1000)
                if f"{model_name}/{subsystem.name}_{i}" not in block_list
            ),
            "",
        )
    if subsystem_full_name in block_list or subsystem_full_name == "":
        return None

    subsystem_path = f"{template_path}/{template_file_name.split('/')[0]}"
    if eng.exist(subsystem_path) != 0.0:
        raise FileNotFoundError("Could not find subsystem template")
    eng.load_system(subsystem_path, nargout=0)
    if "/" in template_file_name:
        eng.load_system(template_file_name, nargout=0)

    subsystem_block_type = SimscapeBlockType.SUBSYSTEM.value

    eng.add_block(subsystem_block_type, subsystem_full_name, nargout=0)
    eng.Simulink.SubSystem.deleteContents(subsystem_full_name, nargout=0)
    __insert_template(eng, template_file_name, subsystem_full_name)

    # set variant labels
    for label, value in template.get_variant_labels(subsystem).items():
        eng.set_param(f"{subsystem_full_name}/{label}", "LabelModeActiveChoice", value, nargout=0)

    # set parameters of components in the template
    # ideally, this would be handled by a central entity that does this for all component types
    component_mapping = template.get_component_mapping(subsystem)
    for component, block_name in component_mapping.items():
        if isinstance(component, IEEEG1):
            set_parameters_ieeeg1(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, HYGOV):
            set_parameters_hygov(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, GAST):
            set_parameters_gast(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, IEEEST1A):
            set_parameters_ieee_st1a(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, SEXS):
            set_parameters_sexs(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, IEEEPSS1A):
            set_parameters_ieee_pss1a(eng, component, f"{subsystem_full_name}/{block_name}")
        elif isinstance(component, IEEEPSS2A):
            set_parameters_ieee_pss2a(eng, component, f"{subsystem_full_name}/{block_name}")

    eng.load_system(subsystem_full_name, nargout=0)

    return SimscapeBlock(subsystem_full_name, SimscapeBlockType.SUBSYSTEM, template)


def insert_subsystem(
    eng: matlab.engine.MatlabEngine, subsystem: Subsystem, model_name: str, base_frequency: float
) -> SimscapeBlock:
    """Inserts a subsystem into the model from the components.

    :param eng: MATLAB engine
    :param subsystem: Subsystem to insert
    :param model_name: Name of the model
    :return: The inserted Subsystem in Simscape
    """

    # Create intermediate model from the components
    random_name = "".join(random.choices(string.ascii_letters, k=10))
    data_stucture = DataStructure(base_frequency=base_frequency, graph=subsystem.graph)
    converter = epowcore.simscape.simscape_converter.SimscapeConverter(eng)
    converter.from_gdf(data_stucture, random_name, apply_rules=False, is_subsystem=True)
    eng.load_system(random_name, nargout=0)
    eng.load_system(model_name, nargout=0)

    subsystem_full_name = f"{model_name}/{subsystem.name}"
    eng.add_block(
        SimscapeBlockType.SUBSYSTEM.value,
        subsystem_full_name,
        nargout=0,
    )
    eng.Simulink.BlockDiagram.copyContentsToSubSystem(
        random_name,
        subsystem_full_name,
        nargout=0,
    )
    os.remove(f"{random_name}.slx")
    return SimscapeBlock(subsystem_full_name, SimscapeBlockType.SUBSYSTEM)


def __insert_template(
    eng: matlab.engine.MatlabEngine, template: str, subsystem_full_name: str
) -> None:
    if "/" in template:
        temp_name = "temp_" + str(hash(time.time()))
        eng.new_system(temp_name)
        # There doesn't seem to be a way to copy the contents of a
        # subsystem to another subsystem directly
        eng.Simulink.SubSystem.copyContentsToBlockDiagram(
            template,
            temp_name,
            nargout=0,
        )
        eng.Simulink.BlockDiagram.copyContentsToSubSystem(
            temp_name,
            subsystem_full_name,
            nargout=0,
        )
    else:
        eng.Simulink.BlockDiagram.copyContentsToSubSystem(
            template,
            subsystem_full_name,
            nargout=0,
        )
