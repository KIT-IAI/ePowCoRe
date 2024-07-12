from epowcore.gdf.component import Component
from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.exciters.sexs import SEXS
from epowcore.gdf.governors.gast import GAST
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.governors.hygov import HYGOV
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A
from epowcore.gdf.power_system_stabilizers.ieee_pss2a import IEEEPSS2A
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.gdf.subsystem import Subsystem
from epowcore.simscape.port_handles import PortHandles
from epowcore.simscape.templates.base_template import SubsystemTemplate


_GOVERNOR_VARIANT_MAPPING: dict[str, str] = {
    "GAST": "gast",
    "HYGOV": "hydro1",
    "IEEEG1": "ieeeg1",
}

_EXCITER_VARIANT_MAPPING: dict[str, str] = {
    "IEEEST1A": "st1a",
    "SEXS": "sexs",
}

_PSS_VARIANT_MAPPING: dict[str, str] = {
    "IEEEPSS1A": "pss1a",
    "IEEEPSS2A": "pss2c",
}


class GeneratorControlsTemplate(SubsystemTemplate):
    """A flexible subsystem with generator controls.
    Allows for various implementations of governor, exciter and PSS.
    """

    template_file_name: str = "generator_controls"
    port_handles: list[PortHandles] = [
        PortHandles("Inport", 0, 1, "m"),
        PortHandles("Outport", 0, 1, "Pm"),
        PortHandles("Outport", 1, 1, "Vf"),
    ]

    @classmethod
    def check_match(cls, subsystem: Subsystem) -> bool:
        num_governors = len([n for n in subsystem.graph.nodes if isinstance(n, Governor)])
        num_exciters = len([n for n in subsystem.graph.nodes if isinstance(n, Exciter)])
        num_pss = len([n for n in subsystem.graph.nodes if isinstance(n, PowerSystemStabilizer)])

        return num_governors == 1 and num_exciters == 1 and num_pss in (0, 1)

    @classmethod
    def get_variant_labels(cls, subsystem: Subsystem) -> dict[str, str]:
        variant_labels: dict[str, str] = {}

        governor = [n for n in subsystem.graph.nodes if isinstance(n, Governor)][0]
        variant_labels["Governor"] = _GOVERNOR_VARIANT_MAPPING[type(governor).__name__]

        exciter = [n for n in subsystem.graph.nodes if isinstance(n, Exciter)][0]
        variant_labels["Exciter"] = _EXCITER_VARIANT_MAPPING[type(exciter).__name__]

        pss = [n for n in subsystem.graph.nodes if isinstance(n, PowerSystemStabilizer)]
        if pss:
            variant_labels["PSS"] = _PSS_VARIANT_MAPPING[type(pss[0]).__name__]
        else:
            variant_labels["PSS"] = "none"

        return variant_labels

    @classmethod
    def get_component_mapping(cls, subsystem: Subsystem) -> dict[Component, str]:
        mapping: dict[Component, str] = {}

        for component in subsystem.graph.nodes:
            if isinstance(component, IEEEG1):
                mapping[component] = "Governor/IEEE G1/Governor Type 1"
            elif isinstance(component, HYGOV):
                mapping[component] = "Governor/Hydro1/Hydro1"
            elif isinstance(component, GAST):
                mapping[component] = "Governor/GAST/GAST"
            elif isinstance(component, IEEEST1A):
                mapping[component] = "Exciter/ST1A"
            elif isinstance(component, SEXS):
                mapping[component] = "Exciter/SEXS/SEXS"
            elif isinstance(component, IEEEPSS1A):
                mapping[component] = "PSS/PSS1A/PSS1A"
            elif isinstance(component, IEEEPSS2A):
                mapping[component] = "PSS/PSS2C/PSS2C"

        return mapping
