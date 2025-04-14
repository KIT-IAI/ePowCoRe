from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.power_factory.to_gdf.components.transformers import WINDING_CONFIG_MAPPING
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.generic.logger import Logger

# The standard WINDING_CONFIG_MAPPING maps pf_value: gdf_value.
# Reversing this mappinng will give us a gdf_value: pf_value mapping to use for the conversion.
REVERSE_WINDING_CONFIG_MAPPING = {v: k for k, v in WINDING_CONFIG_MAPPING.items()}


def create_three_wdg_trafo(self, trafo: ThreeWindingTransformer) -> bool:
    """Convert and add the given gdf core model three winding transformer to the
    given powerfactory network.

    :param trafo: GDF core_model three winding transformer to be converted.
    :type trafo: ThreeWindingTransformer
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    # Get the bus connected to the transformer on the high voltage side
    high_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="HV"
    )[0]
    # Get the bus connected to the transformer on the middle voltage side
    middle_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="MV"
    )
    # Get the bus connected to the transformer on the low voltage side
    low_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="LV"
    )[0]
    # If either bus wasnt found the function failed
    if high_voltage_bus is None or low_voltage_bus is None or middle_voltage_bus is None:
        Logger.log_to_selected(f"Failled to convert three winding transformer {trafo.name}")
        return False
    # Get powerfactory buses
    pf_hv_bus = get_pf_grid_component(self, component_name=high_voltage_bus.name)
    pf_mv_bus = get_pf_grid_component(self, component_name=middle_voltage_bus.name)
    pf_lv_bus = get_pf_grid_component(self, component_name=low_voltage_bus.name)
    # Fails if no powerfactory buses are found
    if pf_hv_bus is None or pf_mv_bus is None or pf_lv_bus is None:
        Logger.log_to_selected(
            f"Three winding transformer {trafo.name} could not be converted because atleast one bus wasn't found."
        )
        return False

    # Create new trafo inside of grid
    pf_trafo = self.pf_grid.CreateObject("ElmTr3", trafo.name)

    # Get transformer types folder
    pf_trafo_type_lib = self.pf_type_library.SearchObject(
        self.pf_type_library.GetFullName() + "\\Transformer Types"
    )
    # Create new type
    pf_trafo_type = pf_trafo_type_lib.CreateObject("TypTr3", trafo.name + "_type")

    # Set attributes for newly created trafo
    pf_trafo_type.SetAttribute("strn3_h", trafo.rating_hv)
    pf_trafo_type.SetAttribute("strn3_m", trafo.rating_mv)
    pf_trafo_type.SetAttribute("strn3_l", trafo.rating_lv)
    pf_trafo_type.SetAttribute("utrn3_h", trafo.voltage_hv)
    pf_trafo_type.SetAttribute("utrn3_m", trafo.voltage_mv)
    pf_trafo_type.SetAttribute("utrn3_l", trafo.voltage_lv)
    pf_trafo_type.SetAttribute("x1_hm", trafo.x1pu_h)
    pf_trafo_type.SetAttribute("x1_ml", trafo.x1pu_m)
    pf_trafo_type.SetAttribute("x1_lh", trafo.x1pu_l)
    pf_trafo_type.SetAttribute("r1_hm", trafo.r1pu_h)
    pf_trafo_type.SetAttribute("r1_ml", trafo.r1pu_m)
    pf_trafo_type.SetAttribute("r1_lh", trafo.r1pu_l)
    pf_trafo_type.SetAttribute("pfe_kw", trafo.pfe_kw)
    pf_trafo_type.SetAttribute("curm3", trafo.no_load_current)
    pf_trafo_type.SetAttribute("tr3cn_h", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_hv])
    pf_trafo_type.SetAttribute("tr3cn_m", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_mv])
    pf_trafo_type.SetAttribute("tr3cn_l", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_lv])
    pf_trafo_type.SetAttribute("nt3ag_h", trafo.phase_shift_30_hv)
    pf_trafo_type.SetAttribute("nt3ag_m", trafo.phase_shift_30_mv)
    pf_trafo_type.SetAttribute("nt3ag_l", trafo.phase_shift_30_lv)

    # Set Connections
    pf_trafo.SetAttribute("bushv", add_cubicle_to_bus(pf_hv_bus))
    pf_trafo.SetAttribute("busmv", add_cubicle_to_bus(pf_mv_bus))
    pf_trafo.SetAttribute("buslv", add_cubicle_to_bus(pf_lv_bus))

    # Set trafo type attribut to the newly created trafo type
    pf_trafo.SetAttribute("typ_id", pf_trafo_type)

    return True


def create_two_wdg_trafo(self, trafo: TwoWindingTransformer) -> bool:
    """Convert and add the given gdf core model two winding transformer to the
    given powerfactory network.

    :param trafo: GDF core_model two winding transformer to be converted.
    :type trafo: TwoWindingTransformer
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    # Get the bus connected to the transformer on the high voltage side
    high_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="HV"
    )[0]
    # Get the bus connected to the transformer on the low voltage side
    low_voltage_bus = self.core_model.get_neighbors(
        component=trafo, follow_links=True, connector="LV"
    )[0]
    # If either bus wasnt found the function failed
    if high_voltage_bus is None or low_voltage_bus is None:
        Logger.log_to_selected(f"Failled to convert two winding transformer {trafo.name}")
        return False
    # Get powerfactory buses
    pf_hv_bus = get_pf_grid_component(self, component_name=high_voltage_bus.name)
    pf_lv_bus = get_pf_grid_component(self, component_name=low_voltage_bus.name)
    # Fails if no powerfactory buses are found
    if pf_hv_bus is None or pf_lv_bus is None:
        Logger.log_to_selected(
            f"Two winding transformer {trafo.name} could not be converted because atleast one bus wasn't found."
        )
        return False

    # Create new trafo inside of grid
    pf_trafo = self.pf_grid.CreateObject("ElmTr2", trafo.name)

    # Get transformer types folder
    pf_trafo_type_lib = self.pf_type_library.SearchObject(
        self.pf_type_library.GetFullName() + "\\Transformer Types"
    )
    # Create new type
    pf_trafo_type = pf_trafo_type_lib.CreateObject("TypTr2", trafo.name + "_type")

    # Set attributes for trafo type of trafo
    pf_trafo_type.SetAttribute("strn", trafo.rating)
    pf_trafo_type.SetAttribute("utrn_h", trafo.voltage_hv)
    pf_trafo_type.SetAttribute("utrn_l", trafo.voltage_lv)
    pf_trafo_type.SetAttribute("r1pu", trafo.r1pu)
    pf_trafo_type.SetAttribute("x1pu", trafo.x1pu)
    pf_trafo_type.SetAttribute("pfe", trafo.pfe_kw)
    pf_trafo_type.SetAttribute("curmg", trafo.no_load_current)
    pf_trafo_type.SetAttribute("tr2cn_h", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_hv])
    pf_trafo_type.SetAttribute("tr2cn_l", REVERSE_WINDING_CONFIG_MAPPING[trafo.connection_type_lv])
    pf_trafo_type.SetAttribute("nt2ag", trafo.phase_shift_30)
    pf_trafo_type.SetAttribute("dutap", trafo.tap_changer_voltage * 100)
    pf_trafo_type.SetAttribute("itapch", 1)  # 1 -> tap on
    pf_trafo_type.SetAttribute("ntpmn", trafo.tap_min)
    pf_trafo_type.SetAttribute("ntpmx", trafo.tap_max)
    pf_trafo_type.SetAttribute("nntap0", trafo.tap_neutral)

    # Set attribute of trafo itself
    pf_trafo.SetAttribute("nntap", trafo.tap_initial)  # Attribute of the transformer itself
    # Set trafo type attribut to the newly created trafo type
    pf_trafo.SetAttribute("typ_id", pf_trafo_type)

    # Set Connections
    pf_trafo.SetAttribute("bushv", add_cubicle_to_bus(pf_hv_bus))
    pf_trafo.SetAttribute("buslv", add_cubicle_to_bus(pf_lv_bus))

    return True
