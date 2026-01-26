from epowcore.gdf.tline import TLine
from epowcore.power_factory.utils import get_pf_grid_component, add_cubicle_to_bus
from epowcore.generic.logger import Logger


def create_line(self, tline: TLine) -> bool:
    """Convert and add the given gdf core model tline to the given powerfactory network.

    :param tline: GDF core_model tline to be converted.
    :type tline: TLine
    :return: Return true if the conversion suceeded, false if it didn't.
    :rtype: bool
    """
    success = True

    # Create new line inside of grid
    pf_line = self.pf_grid.CreateObject("ElmLne", tline.name)

    from_bus = self.core_model.get_neighbors(component=tline, follow_links=True, connector="A")[0]
    to_bus = self.core_model.get_neighbors(component=tline, follow_links=True, connector="B")[0]
    if from_bus is None or to_bus is None:
        Logger.log_to_selected(
            f"At least one bus not found inside of the gdf for tline {tline.name}"
        )
        success = False

    # Get powerfactory buses
    pf_from_bus = get_pf_grid_component(self, component_name=from_bus.name)
    pf_to_bus = get_pf_grid_component(self, component_name=to_bus.name)

    if pf_from_bus is None or pf_to_bus is None:
        Logger.log_to_selected(
            f"At least one bus not found inside of powerfactory for tline {tline.name}"
        )
        success = False

    # Set connections
    pf_line.SetAttribute("bus1", add_cubicle_to_bus(pf_from_bus))
    pf_line.SetAttribute("bus2", add_cubicle_to_bus(pf_to_bus))

    # Helper function for converting zero sequence values that use None inside of the gdf
    def zero_sequence_transform(a):
        return 0 if a is None else a

    # Get line types folder
    pf_line_type_lib = self.pf_type_library.SearchObject(
        self.pf_type_library.GetFullName() + "\\Line Types"
    )
    # Create new type
    pf_line_type = pf_line_type_lib.CreateObject("TypLne", tline.name + "_type")
    # Set attribtes for line type of line
    pf_line_type.SetAttribute("rline", tline.r1)
    pf_line_type.SetAttribute("xline", tline.x1)
    pf_line_type.SetAttribute("bline", tline.b1)
    pf_line_type.SetAttribute("uline", pf_from_bus.GetAttribute("uknom"))
    pf_line_type.SetAttribute("sline", tline.rating / pf_from_bus.GetAttribute("uknom"))
    pf_line_type.SetAttribute("rline0", zero_sequence_transform(tline.r0))
    pf_line_type.SetAttribute("xline0", zero_sequence_transform(tline.x0))
    pf_line_type.SetAttribute("bline0", zero_sequence_transform(tline.b0))

    # Set attributes of line itself
    pf_line.SetAttribute("nlnum", tline.parallel_lines)
    pf_line.SetAttribute("dline", tline.length)
    pf_line.SetAttribute("loc_name", tline.name)
        #lat = [x[0] for x in obj.GPScoords if len(x) > 1]
        #lon = [x[1] for x in obj.GPScoords if len(x) > 1]
    if  tline.coords is not None:
        pf_line.GPScoords = [[coords[0],coords[1]] for coords in tline.coords]
    # Set line type attribut to the newly crated line type
    pf_line.SetAttribute("typ_id", pf_line_type)

    return success
