from dataclasses import dataclass

from epowcore.generic.configuration import Configuration
from epowcore.simscape.port_handles import PORT_HANDLES, PortHandles
from epowcore.simscape.shared import SimscapeBlockType


@dataclass
class GroupRuleComponent:
    """A component of a group rule."""

    component: str
    distance: int
    connections: list[str]


@dataclass
class GroupSubsystemRule:
    """A grouping rule for subsystems."""

    name: str
    priority: int
    rules: list[GroupRuleComponent]
    include_inner: bool
    remove_inner: bool = False


class ConfigManager:
    """Conversion and caching of contents of the configuration file."""

    _group_subsystem_rules: list[GroupSubsystemRule] | None = None

    @staticmethod
    def group_subsystem_rules() -> list[GroupSubsystemRule]:
        """All grouping rules.

        :return: The grouping rules.
        """
        if not ConfigManager._group_subsystem_rules:
            ConfigManager._group_subsystem_rules = []
            for r in Configuration().get("GDF.GroupRules"):
                if any(
                    x not in r.keys() for x in ["name", "priority", "rules"]
                ) or not all(  # Check GroupSubsystemRule
                    all(y in x.keys() for y in ["component", "distance", "connections"])
                    for x in r["rules"]  # Check GroupRuleComponent
                ):
                    raise ValueError(
                        "Grouping rules must have the keys 'name', 'priority' and 'rules'."
                    )
                if r["inner"] not in ("include", "remove", "ignore"):
                    r["inner"] = "ignore"
                ConfigManager._group_subsystem_rules.append(
                    GroupSubsystemRule(
                        r["name"],
                        r["priority"],
                        [
                            GroupRuleComponent(c["component"], c["distance"], c["connections"])
                            for c in r["rules"]
                        ],
                        r["inner"] == "include",
                        r["inner"] == "remove",
                    )
                )

        return ConfigManager._group_subsystem_rules

    @staticmethod
    def get_specific_porthandles(
        block_type: SimscapeBlockType, port_name: str
    ) -> PortHandles | None:
        """Get the port handles for a specific port of a block type and GDF port name.

        :param block_type: The block type.
        :param port_name: The GDF port name.
        :return: The port handles or None if not defined or on error.
        """
        return PORT_HANDLES.get(block_type, {}).get(port_name)

    @staticmethod
    def get_all_porthandles(block_type: SimscapeBlockType) -> list[PortHandles] | None:
        """Return all port handles for a block type.

        :param block_type: The block type.
        :return: The port handles or None if not defined or on error.
        """
        handles = PORT_HANDLES.get(block_type)
        if handles is None:
            return None
        return list(handles.values())
