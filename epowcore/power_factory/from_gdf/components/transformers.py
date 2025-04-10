from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.power_factory.to_gdf.components.transformers import WINDING_CONFIG_MAPPING
from epowcore.power_factory.utils import get_pf_component
from epowcore.generic.logger import Logger

# The standard WINDING_CONFIG_MAPPING maps pf_value: gdf_value.
# Reversing this mappinng will give us a gdf_value: pf_value mapping to use for the conversion.
REVERSE_WINDING_CONFIG_MAPPING = {v: k for k, v in WINDING_CONFIG_MAPPING.items()}


def create_three_wdg_trafo(
    self, trafo: ThreeWindingTransformer
) -> bool:
    """Convert and add the given gdf core model three winding transformer to the
    given powerfactory network.

    :param pf_project: Powerfactory project object to create a new object.
    :type pf_project: pf.DataObject
    :param core_model: GDF core_model used to search the load bus.
    :type core_model: CoreModel
    :param trafo: GDF core_model three winding transformer to be converted.
    :type trafo: TwoWindingTransformer
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """

    # Get the bus connected to the transformer on the high voltage side
    high_voltage_bus = self.core_model.get_neighbors(component=trafo, follow_links=True, connector="HV")[
        0
    ]
    # Get the bus connected to the transformer on the middle voltage side
    middle_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="MV"
    )
    # Get the bus connected to the transformer on the low voltage side
    low_voltage_bus = self.core_model.get_neighbors(component=trafo, follow_links=True, connector="LV")[
        0
    ]
    # If either bus wasnt found the function failed
    if high_voltage_bus is None or low_voltage_bus is None or middle_voltage_bus is None:
        Logger.log_to_selected(f"Failled to convert three winding transformer {trafo.name}")
        return False
    # Get powerfactory buses
    pf_hv_bus = get_pf_component(
        app=self.app, component_type="ElmTr3", component_name=high_voltage_bus.name
    )
    pf_mv_bus = get_pf_component(
        app=self.app, component_type="ElmTr3", component_name=middle_voltage_bus.name
    )
    pf_lv_bus = get_pf_component(
        app=self.app, component_type="ElmTr3", component_name=low_voltage_bus.name
    )
    # Fails if no powerfactory buses are found
    if pf_hv_bus == [] or pf_mv_bus == [] or pf_lv_bus == []:
        Logger.log_to_selected(
            f"Three winding transformer {trafo.name} could not be converted because atleast one bus wasn't found."
        )
        return False

    # Create trafo inside of network
    pf_trafo = self.pf_project.CreateObject("ElmTr3")

    # Set Connections
    pf_trafo.SetAttribute("bushv", pf_hv_bus)
    pf_trafo.SetAttribute("busmv", pf_mv_bus)
    pf_trafo.SetAttribute("buslv", pf_lv_bus)

    # Set attributes for newly created trafo
    pf_trafo.SetAttribute("strn3_h", trafo.rating_hv)
    pf_trafo.SetAttribute("strn3_m", trafo.rating_mv)
    pf_trafo.SetAttribute("strn3_l", trafo.rating_lv)
    pf_trafo.SetAttribute("utrn3_h", trafo.voltage_hv)
    pf_trafo.SetAttribute("utrn3_m", trafo.voltage_mv)
    pf_trafo.SetAttribute("utrn3_l", trafo.voltage_lv)
    pf_trafo.SetAttribute("x1_hm", trafo.x1pu_h)
    pf_trafo.SetAttribute("x1_ml", trafo.x1pu_m)
    pf_trafo.SetAttribute("x1_lh", trafo.x1pu_l)
    pf_trafo.SetAttribute("r1_hm", trafo.r1pu_h)
    pf_trafo.SetAttribute("r1_ml", trafo.r1pu_m)
    pf_trafo.SetAttribute("r1_lh", trafo.r1pu_l)
    pf_trafo.SetAttribute("pfe_kw", trafo.pfe_kw)
    pf_trafo.SetAttribute("curm3", trafo.no_load_current)
    pf_trafo.SetAttribute("tr3cn_h", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_hv])
    pf_trafo.SetAttribute("tr3cn_m", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_mv])
    pf_trafo.SetAttribute("tr3cn_l", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_lv])
    pf_trafo.SetAttribute("nt3ag_h", trafo.phase_shift_30_hv)
    pf_trafo.SetAttribute("nt3ag_m", trafo.phase_shift_30_mv)
    pf_trafo.SetAttribute("nt3ag_l", trafo.phase_shift_30_lv)

    return True


def create_two_wdg_trafo(
    self, trafo: TwoWindingTransformer
) -> bool:
    """Convert and add the given gdf core model two winding transformer to the
    given powerfactory network.

    :param pf_project: Powerfactory pf_project object to create a new object.
    :type pf_project: pf.DataObject
    :param core_model: GDF core_model used to search the load bus.
    :type core_model: CoreModel
    :param trafo: GDF core_model two winding transformer to be converted.
    :type trafo: TwoWindingTransformer
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    # Get the bus connected to the transformer on the high voltage side
    high_voltage_bus = self.core_model.get_neighbors(component=trafo, follow_links=True, connector="HV")[
        0
    ]
    # Get the bus connected to the transformer on the low voltage side
    low_voltage_bus = self.core_model.get_neighbors(component=trafo, follow_links=True, connector="LV")[
        0
    ]
    # If either bus wasnt found the function failed
    if high_voltage_bus is None or low_voltage_bus is None:
        Logger.log_to_selected(f"Failled to convert two winding transformer {trafo.name}")
        return False
    # Get powerfactory buses
    pf_hv_bus = get_pf_component(
        app=self.app, component_type="ElmTr3", component_name=high_voltage_bus.name
    )
    pf_lv_bus = get_pf_component(
        app=self.app, component_type="ElmTr3", component_name=low_voltage_bus.name
    )
    # Fails if no powerfactory buses are found
    if pf_hv_bus == [] or pf_lv_bus == []:
        Logger.log_to_selected(
            f"Two winding transformer {trafo.name} could not be converted because atleast one bus wasn't found."
        )
        return False

    # Create trafo inside of network
    pf_trafo = self.pf_project.CreateObject("ElmTr3")

    # Set Connections
    pf_trafo.SetAttribute("bushv", pf_hv_bus)
    pf_trafo.SetAttribute("buslv", pf_lv_bus)

    # Set attributes for newly created trafo
    pf_trafo.SetAttribute("strn", trafo.rating)
    pf_trafo.SetAttribute("utrn_h", trafo.voltage_hv)
    pf_trafo.SetAttribute("utrn_l", trafo.voltage_lv)
    pf_trafo.SetAttribute("r1pu", trafo.r1pu)
    pf_trafo.SetAttribute("x1pu", trafo.x1pu)
    pf_trafo.SetAttribute("pfe", trafo.pfe_kw)
    pf_trafo.SetAttribute("curmg", trafo.no_load_current)
    pf_trafo.SetAttribute("tr2cn_h", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_hv])
    pf_trafo.SetAttribute("tr2cn_l", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_lv])
    pf_trafo.SetAttribute("nt2ag", trafo.phase_shift_30)
    pf_trafo.SetAttribute("dutap", trafo.tap_changer_voltage * 100)
    pf_trafo.SetAttribute("ntpmn", trafo.tap_min)
    pf_trafo.SetAttribute("ntpmx", trafo.tap_max)
    pf_trafo.SetAttribute("nntap0", trafo.tap_neutral)
    pf_trafo.SetAttribute("nntap", trafo.tap_initial)

    return True
