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


def get_pf_component(
    app: pf.Application, component_type: str, component_name: str | None = None
) -> pf.DataObject | list[pf.DataObject] | None:
    """Function to get a reference to a certain component or multiple components 
    in the powerfactory network of the app.
    The component type must be specified for the search and the component 
    name can also be specified.


    :param app: Powerfactory application instance to run functions on.
    :type app: pf.Application
    :param component_type: Powerfactory type of the components to get.
    :type component_type: str
    :param component_name: Component name for getting components of type and name, defaults to none.
    :type component_name: str | None
    :return: Returns the powerfactory component or a list of components if multiple were found.
    :rtype: pf.DataObject | list[pf.DataObject]
    """
    component_list = app.GetCalcRelevantObjects(component_type)
    if component_name is None:
        if component_list == []:
            return None
        return component_list

    component_list = [
        component for component in component_list if component.loc_name == component_name
    ]
    if component_list == []:
        return None
    return component_list
