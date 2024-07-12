from epowcore.gdf.component import Component
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.configuration import Configuration
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.controller_grouping import SMControllerGrouping
from epowcore.generic.manipulation.subsystem_grouping import SubsystemGrouping

AVAILABLE_GROUPINGS: dict[str, SubsystemGrouping] = {
    "SM_CONTROLLERS": SMControllerGrouping(),
}


def apply_group_subsystem_rules(
    data_structure: DataStructure
) -> list[Subsystem]:
    """Applies the rules for grouping subsystems from the configuration.

    :param data_structure: The data structure to apply the rules to.
    :type data_structure: DataStructure
    :param rule_list: The list of rules to apply. If empty, all rules are applied.
    :type rule_list: list[str]
    :return: The subsystems that were created.
    """
    config = Configuration().get("Global.SUBSYSTEM_GROUPINGS")
    groupings = [AVAILABLE_GROUPINGS[g] for g in config]
    subsystems: list[Subsystem] = []
    for grouping in groupings:
        subsystems.extend(__apply_rule(grouping, data_structure))
    return subsystems


def __apply_rule(rule: SubsystemGrouping, data_structure: DataStructure) -> list[Subsystem]:
    """Applies a grouping rule to the data structure.

    :param rule: The rule to apply.
    :param data_structure: The data structure to apply the rule to.
    :type data_structure: DataStructure
    :return: The subsystems that were created.
    :rtype: list[Subsystem]
    """
    subsystems: list[Subsystem] = []
    grouped_components: set[Component] = set()
    # check every component as core for the grouping
    for component in data_structure.component_list():
        # check that the potential core component has not been grouped already
        if component not in grouped_components:
            comps_to_group = rule.check_match(component, data_structure)
            # check that all components that should be grouped have not been grouped already
            if comps_to_group is not None and not any(
                c in grouped_components for c in comps_to_group
            ):
                subsystem = Subsystem.from_components(
                    data_structure,
                    comps_to_group,
                    name=rule.get_name(component, data_structure, comps_to_group),
                )
                if subsystem is not None:
                    grouped_components.update(comps_to_group)
                    subsystems.append(subsystem)

    if len(subsystems) > 0:
        Logger.log_to_selected(f"Applied rule {rule.name} and created {len(subsystems)} subsystems")
    return subsystems
