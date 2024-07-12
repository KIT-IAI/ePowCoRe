from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.generic.manipulation.subsystem_grouping import SubsystemGrouping


class SMControllerGrouping(SubsystemGrouping):
    """Group together controllers (governor, exciter, PSS)
    that are connected to the same synchronous machine.
    """

    name: str = "SM Controller Grouping"

    @classmethod
    def check_match(cls, core_component: Component, ds: DataStructure) -> list[Component] | None:
        if not isinstance(core_component, SynchronousMachine):
            return None

        # get all components connected to the generator; only apply when they are on the same level
        neighbors = ds.get_neighbors(core_component, follow_links=False)

        govs = [n for n in neighbors if isinstance(n, Governor)]
        excs = [n for n in neighbors if isinstance(n, Exciter)]
        psss = [n for n in neighbors if isinstance(n, PowerSystemStabilizer)]

        # check if the following components are connected to the sync machine:
        # 1 governor, 1 exciter, and optionally 1 PSS
        if len(govs) == 1 and len(excs) == 1 and len(psss) < 2:
            return govs + excs + psss  # type: ignore
        return None

    @classmethod
    def get_name(
        cls, core_component: Component, ds: DataStructure, components: list[Component]
    ) -> str:
        return f"Control {core_component.name}"
