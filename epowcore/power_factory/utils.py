import powerfactory as pf
from typing import Any


def get_coords(obj: Any) -> tuple[float, float] | list[tuple[float, float]] | None:
    """Try to get the coordinates of a given PowerFactory object."""
    if not (hasattr(obj, "GPSlat") and hasattr(obj, "GPSlon")) and not hasattr(obj, "GPScoords"):
        return None
    if hasattr(obj, "GPScoords"):
        lat = [x[0] for x in obj.GPScoords if len(x) > 1]
        lon = [x[1] for x in obj.GPScoords if len(x) > 1]
        if len(lat) == 0 or len(lon) == 0:
            return None
        return list(zip(lat, lon))
    if obj.GPSlat == 0.0 and obj.GPSlon == 0.0:
        return None
    return (obj.GPSlat, obj.GPSlon)


def get_ctrl_param(ctrl_obj: Any, param: str | list[str]) -> Any:
    """Retrieve a parameter value of a given control component (e.g. governor, exciter,...) by name.

    Supports either one parameter name or a list of alternative parameter names.

    :param ctrl_obj: The control component to get the parameter value from.
    :type ctrl_obj: DataObject
    :param param: The single parameter name or list of names.
    :type param: str | list[str]
    :raises TypeError: If parameters of control component are not a list.
    :raises ValueError: If the given parameter name is not found in the control component.
    :return: The value of the parameter.
    :rtype: Any
    """
    model_params = ctrl_obj.GetAttribute("parameterNames")
    if not isinstance(model_params, list):
        raise TypeError("Expected params to be a list: ['A,B,C']")
    model_params = model_params[0].split(",")

    if isinstance(param, str):
        if param not in model_params:
            raise ValueError(f"{param=} not found in parameter list: {model_params}")
        return ctrl_obj.GetAttribute(f"e:params:{param}")

    for p in param:
        if p in model_params:
            return ctrl_obj.GetAttribute(f"e:params:{p}")
    raise ValueError(f"No corresponding value found in parameter list: {model_params}")


def get_pf_grid_component(self, component_name: str) -> pf.DataObject | None:
    """Gets a component from the pf_grid by it's name.

    :param component_name: Components name, defined by its loc_name variable
    :type component_name: str
    :return: Returns a reference to the object or none, if no object of the given name was found
    :rtype: pf.DataObject | None
    """
    component = self.pf_grid.SearchObject(self.pf_grid.GetFullName() + "\\" + component_name)

    if component is None or not isinstance(component, pf.DataObject):
        return None
    return component


def add_cubicle_to_bus(bus: pf.DataObject) -> pf.DataObject:
    """Adds a cubicle to the given bus, connects the cubicle to the bus and returns a reference to it.

    :param bus: powerfactory bus to add the cubicle to
    :type bus: pf.DataObject
    :return: Returns a reference to the newly added cubicle
    :rtype: pf.DataObject
    """
    cubicles = bus.GetConnectedCubicles(1)
    cubicle = bus.CreateObject("StaCubic", f"{bus.loc_name}_Cub_{len(cubicles) + 1}")
    # The bus of the cubicle (cterm attribute) is automatically set
    return cubicle
