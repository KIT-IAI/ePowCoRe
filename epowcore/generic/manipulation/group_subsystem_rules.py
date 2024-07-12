from epowcore.gdf.component import Component
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.configuration import Configuration
from epowcore.generic.logger import Logger
from epowcore.generic.manipulation.controller_grouping import SMControllerGrouping
from epowcore.generic.manipulation.subsystem_grouping import SubsystemGrouping

AVAILABLE_GROUPINGS: dict[str, SubsystemGrouping] = {
    "SM_CONTROLLERS": SMControllerGrouping(),
}


def apply_group_subsystem_rules(
    core_model: CoreModel
) -> list[Subsystem]:
    """Applies the rules for grouping subsystems from the configuration.

    :param core_model: The core model to apply the rules to.
    :type core_model: CoreModel
    :param rule_list: The list of rules to apply. If empty, all rules are applied.
    :type rule_list: list[str]
    :return: The subsystems that were created.
    """
    config = Configuration().get("Global.SUBSYSTEM_GROUPINGS")
    groupings = [AVAILABLE_GROUPINGS[g] for g in config]
    subsystems: list[Subsystem] = []
    for grouping in groupings:
        subsystems.extend(__apply_rule(grouping, core_model))
    return subsystems


def __apply_rule(rule: SubsystemGrouping, core_model: CoreModel) -> list[Subsystem]:
    """Applies a grouping rule to the core model.

    :param rule: The rule to apply.
    :param core_model: The core model to apply the rule to.
    :type core_model: CoreModel
    :return: The subsystems that were created.
    :rtype: list[Subsystem]
    """
    subsystems: list[Subsystem] = []
    grouped_components: set[Component] = set()
    # check every component as core for the grouping
    for component in core_model.component_list():
        # check that the potential core component has not been grouped already
        if component not in grouped_components:
            comps_to_group = rule.check_match(component, core_model)
            # check that all components that should be grouped have not been grouped already
            if comps_to_group is not None and not any(
                c in grouped_components for c in comps_to_group
            ):
                subsystem = Subsystem.from_components(
                    core_model,
                    comps_to_group,
                    name=rule.get_name(component, core_model, comps_to_group),
                )
                if subsystem is not None:
                    grouped_components.update(comps_to_group)
                    subsystems.append(subsystem)

    if len(subsystems) > 0:
        Logger.log_to_selected(f"Applied rule {rule.name} and created {len(subsystems)} subsystems")
    return subsystems
