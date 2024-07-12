import networkx as nx
from pyapi_rts.api import (
    Draft,
    Component,
    Hierarchy,
    Subsystem,
)
from pyapi_rts.generated.stickynotedef import (
    stickynotedef as stickyNote,
)
from pyapi_rts.api.lark.rlc_tline import RLCTLine
from pyapi_rts.generated.rtdsriscNET import rtdsriscNET

from epowcore.generic.logger import Logger
from epowcore.rscad.constants import GRID_OFFSET, GRID_STEP_SIZE

from .graph_transformer_rscad import GraphTransformerRscad
from . import rscad_connection_setter as connection_setter
from .canvas_drawer_helpers import (
    add_elements_to_hierarchy,
    create_hierarchy,
    get_all_subgraphs,
    get_connections_dict,
    round_to_multiple,
    update_hierarchy_size,
)

# Used to filter out components that should not be packed into bus hierarchies.
# This mostly applies to components connecting multiple buses.
UNWANTED_BUS_CONNECTIONS = [
    "_rtds_3P2W_TRF.def",
    "_rtds_3P3W_TRF.def",
    "lf_rtds_sharc_sld_SERIESRLC",
    "_rtds_PI123.def",
]

GENERATOR_CONTROLS = [
    "_rtds_PTIST1.def",
    "_rtds_EXST1A.def",
    "_rtds_IEEEG1.def",
    "_rtds_IEEET1.def",
    "_rtds_PSS1A.def",
]

REQUIRED_ROTATION = {
    "rtds_udc_DYLOAD": 3,
}


class RscadCanvasDrawer:
    """This class uses a networkX graph of Rscad Components to draw Rscad components onto a canvas.
    The result is a valid model.
    """

    def __init__(
        self,
        graph: nx.Graph,
        draft: Draft,
        graph_manager: GraphTransformerRscad,
        tli_files: list[RLCTLine],
    ):
        # Graph of Rscad elements with "abstract" connections
        self.graph = graph
        # Draft file where the Rscad project resides in
        self.draft = draft
        self.subsystem = self.draft.subsystems[0]
        self.graph_manager = graph_manager
        self.tli_files = tli_files

    def draw_elements_on_canvas(self) -> None:
        """Place all elements onto their final position on the grid."""
        self.generators_to_hierarchy()
        self.buses_to_hierarchy()
        self.bus_hierarchies_to_hierarchy()
        self.place_last_bus_boxes(self.subsystem)

    def generators_to_hierarchy(self) -> None:
        """Aggregate every Generator to a hierarchy box with its connected control elements and bus."""
        # TODO: Extend for each Generator type in the generic core model
        generators = self.draft.get_components_by_type("lf_rtds_sharc_sld_MACV31", False)
        # Go through each Generator
        for gen in generators:
            # Get the connections of all immediate neighbors to aggregate them in the hierarchy box
            connected = self.graph.neighbors(gen.uuid)
            filtered = []
            bus_label = None
            for component_id in connected:
                # explicitly gather the bus connected to the generator
                component = self.draft.get_by_id(component_id)
                if component is None:
                    continue
                if component.type == "rtds_sharc_sld_BUSLABEL":
                    bus_label = component
                    if bus_label is None:
                        raise ValueError(f"BusLabel {component.name} not found in subsystem")
                    # Set voltage point for the connected generator
                    bus_label.LOADFLOWDATA.Vi.value = (  # type: ignore
                        gen.MACHINEINITIALLOADFLOWDATA.Vmagn.value  # type: ignore
                    )

                if component.type in GENERATOR_CONTROLS:
                    filtered.append(component)
            if bus_label is None:
                raise ValueError(f"BusLabel for Generator {gen.name} not found in subsystem")
            hierarchy_box = self.pack_generator_to_hierarchy(gen, bus_label, filtered)
            # Add the new hierarchy box to subsytem
            self.subsystem.add_component(hierarchy_box)

    def pack_generator_to_hierarchy(
        self, gen: Component, bus_label: Component, components: list[Component]
    ) -> Hierarchy:
        """Packs the list of components with its relevant generator and bus into one hierarchy box."""
        # Create Hierarchy Box
        generator_box = create_hierarchy(gen.name)
        sub_graph = self.graph_manager.get_subgraph(components + [gen, bus_label], self.graph)
        Logger.log_to_selected(
            f"Generator {gen.name} is converted to a hierarchy box with {len(components) + 2} components."
        )
        # sub_graph = nx.subgraph(self.graph, components + [gen, bus_label])
        to_remove = self.graph_manager.replace_subgraph(
            self.graph, sub_graph, generator_box, self.draft, bus_label
        )
        self.generator_box_placing(generator_box, gen, bus_label, components)
        self.remove_from_draft_by_id(to_remove)
        return generator_box

    def generator_box_placing(
        self,
        generator_box: Hierarchy,
        generator: Component,
        bus_label: Component,
        components: list[Component],
    ) -> None:
        """Places the elements inside the hierarchy box of for the direct generator elements.

        As the possible elements inside this box are almost always similar,
        they can be placed on predefined places on the grid.
        When generators, other than the MACV31, are supported by the converter
        it is possible that the grid positions have to be altered
        depending of the type of generator."""
        # Connection elements to add to the hierarchy box
        connecting_items = []
        # Set generator position
        generator.x = GRID_OFFSET + GRID_STEP_SIZE * 16
        generator.y = GRID_OFFSET + GRID_STEP_SIZE * 16
        bus_distance = GRID_STEP_SIZE * 10
        control_distance = 7 * GRID_STEP_SIZE
        connection_coordinates = connection_setter.get_connection_point_coordinates(
            generator, "A_1"
        )
        # Duplicate the bus to have a new independant instance
        bus_label_duplicate = bus_label.duplicate(new_id=True)
        # Set orientation and position of duplicated bus
        bus_label_duplicate.rotation = 1
        bus_label_duplicate.x = connection_coordinates[0] + bus_distance
        bus_label_duplicate.y = connection_coordinates[1]
        # Set initial position for the rest of the elements in components
        x = GRID_OFFSET + GRID_STEP_SIZE * 3
        y = GRID_OFFSET + GRID_STEP_SIZE * 5
        # Set the position of the elements in components
        for component in components:
            component.x = x
            component.y = y
            x += control_distance
        connecting_items += connection_setter.set_wire_points_generator_box(
            [generator] + components, (bus_label_duplicate.x, bus_label_duplicate.y)
        )
        add_elements_to_hierarchy(
            generator_box,
            components + [generator],
            self.graph_manager,
            bus_label_duplicate,
            connecting_items,
        )

    def buses_to_hierarchy(self) -> None:
        """Aggregates every bus with its connections into a hierarchyBox.

        Connections are filtered by type according to UNWANTED_BUS_CONNECTIONS.
        Components of these types are not included in the hierarchies.
        """
        buses = self.draft.get_components_by_type("rtds_sharc_sld_BUSLABEL", False)
        for bus in buses:
            # Get the connections of all immediate neighbors to aggregate them in the hierarchy box
            connected = self.graph.neighbors(bus.uuid)
            filtered = [self.subsystem.get_by_id(element) for element in connected]
            filtered = [
                element
                for element in filtered
                if element is not None and not element.type in UNWANTED_BUS_CONNECTIONS
            ]
            if len(filtered) == 0:
                continue
            hierarchy_box = self.pack_bus_to_hierarchy(bus, filtered)
            self.subsystem.add_component(hierarchy_box)

    def pack_bus_to_hierarchy(self, bus: Component, components: list[Component]) -> Hierarchy:
        """Packs the list of components into one hierarchy box representing the Bus."""
        bus_box = create_hierarchy(bus.name)
        sub_graph = self.graph_manager.get_subgraph(components + [bus], self.graph)
        to_remove = self.graph_manager.replace_subgraph(
            self.graph, sub_graph, bus_box, self.draft, bus
        )
        self.bus_box_placing(bus_box, bus, components)
        self.remove_from_draft_by_id(to_remove)
        update_hierarchy_size(bus_box)
        return bus_box

    def bus_box_placing(
        self, bus_box: Hierarchy, bus_label: Component, components: list[Component]
    ) -> None:
        """Strategy to place elements inside a bus hierarchy box and connect them with the bus.

        The busLabel is placed on the top with a main busLine going down.
        The components are placed alongside the main busLine on the left.
        """
        # Connection elements to add to the hierarchy box
        connecting_items = []
        # Duplicate the busLabel for a different instance
        bus_label_duplicate = bus_label.duplicate(new_id=True)
        # Set orientation and position of duplicated bus
        bus_label_duplicate.x = GRID_OFFSET + GRID_STEP_SIZE * 5
        bus_label_duplicate.y = GRID_OFFSET + GRID_STEP_SIZE * 4
        # Distance of the components to the "main" busline in x-direction
        x_distance_to_base_bus = GRID_STEP_SIZE * 10
        # Distance between the components in y-direction
        y_distance_components = GRID_STEP_SIZE * 10
        # Length of the main connecting busline depending on the amount of components
        base_bus_line_length = len(components) * y_distance_components + GRID_OFFSET
        component_y_position = GRID_OFFSET + GRID_STEP_SIZE * 10
        x_position = bus_label_duplicate.x + x_distance_to_base_bus
        # Create the main busline and add it to the list of connection elements
        connecting_items.append(
            connection_setter.create_bus_connection(
                (bus_label_duplicate.x, bus_label_duplicate.y + GRID_STEP_SIZE),
                (bus_label_duplicate.x + base_bus_line_length, bus_label_duplicate.y),
                "y",
            )
        )
        # Place each component and connect it to the main busline
        for component in components:
            component_borders = component.bounding_box  # TODO: MW not sure about this
            # Check if an element is a TLine to put the connection to the bus into a dictionary
            if component.type == "lf_rtds_sharc_sld_TLINE":
                self.graph_manager.line_connection_graph[bus_box.uuid].append(
                    component.CONFIGURATION.Tnam1.value  # type: ignore
                )

            component.rotation = REQUIRED_ROTATION.get(component.type, 0)
            # Get connection position by the x position plus the border position of the appropriate component
            component.x = x_position + round_to_multiple(
                abs(component_borders[0 + component.rotation]),
                GRID_STEP_SIZE,  # TODO: MW not sure about this
            )
            component.y = component_y_position
            # Create connection to the right side
            connection_pos = next(
                filter(
                    (
                        lambda x: int(x[0]) == bus_label_duplicate.x + x_distance_to_base_bus
                        and int(x[1]) == component_y_position
                    ),
                    component.generate_pos_dict().keys(),
                ),
                None,
            )
            if connection_pos is not None:
                connecting_items.append(
                    connection_setter.create_bus_connection(
                        (bus_label_duplicate.x + GRID_STEP_SIZE, component_y_position),
                        (
                            int(connection_pos[0]),
                            int(connection_pos[1]),
                        ),
                        "x",
                    )
                )
            component_y_position += y_distance_components
        add_elements_to_hierarchy(
            bus_box,
            components,
            self.graph_manager,
            bus_label_duplicate,
            connecting_items,
        )

    def bus_hierarchies_to_hierarchy(self) -> None:
        """Puts Bus hierarchies which are connected to other bus hierarchy (e.g. via a transformer)
        together into a new hierarchy box"""
        subgraphs = get_all_subgraphs(self.graph)
        # Buses that are connected are inside the same subgraph
        for subgraph in subgraphs:
            # Bus is otherwise not connected with another bus, no new hierarchy needed
            if len(subgraph.nodes) <= 2:
                continue
            # Temporary name
            hierarchy = create_hierarchy("Busbox")
            # Get all components inside the subgraph by the uuid
            components = []
            for component_id in subgraph:
                components.append(self.draft.get_by_id(component_id))
            to_remove = self.graph_manager.replace_single_subgraph(self.graph, subgraph, hierarchy)
            self.place_in_hierarchy(hierarchy, components, subgraph)
            self.remove_from_draft_by_id(to_remove)
            update_hierarchy_size(hierarchy)
            self.subsystem.add_component(hierarchy)

    def place_in_hierarchy(
        self,
        parent_hierarchy: Hierarchy,
        components: list[Component],
        subgraph: nx.Graph,
    ) -> None:
        """Places the components inside the hierarchy box after filtering them by their type"""
        bus_labels = []
        hierarchies = []
        connecting_components = []
        for component in components:
            if component is not None:
                if component.type == "rtds_sharc_sld_BUSLABEL":
                    bus_labels.append(component)
                elif component.type == "HIERARCHY":
                    hierarchies.append(component)
                else:
                    connecting_components.append(component)
        # Sort the bus hierarchy boxes by their name
        hierarchies.sort(key=lambda x: x.BoxParameters.Name.value)
        self.__hierarchy_box_placing(
            parent_hierarchy, bus_labels, hierarchies, connecting_components, subgraph
        )

    def __hierarchy_box_placing(
        self,
        parent_hierarchy: Hierarchy,
        bus_labels: list[Component],
        hierarchies: list[Hierarchy],
        connecting_components: list[Component],
        subgraph: nx.Graph,
    ) -> None:
        """Place the busLabels, hierarchy boxes and connectiong bus components inside the hierarchy box"""
        # Position dictionary for connections between components
        connections_dict = {}
        # Initial positions for each type of component
        initial_x_bus_labels = GRID_OFFSET + GRID_STEP_SIZE * 4
        y_bus_labels = GRID_OFFSET + GRID_STEP_SIZE * 7
        initial_x_hierarchies = GRID_OFFSET + GRID_STEP_SIZE * 4
        y_hierarchies = GRID_OFFSET + GRID_STEP_SIZE * 3
        initial_x_others = GRID_OFFSET + GRID_STEP_SIZE * 6
        y_others = GRID_OFFSET + GRID_STEP_SIZE * 13
        # Collect the names of the bus hierarchies to name the parent hierarchy box
        parent_name = ""
        additional_bus_labels: list = []
        # Place each type of component on the grid
        parent_name = ", ".join([str(x.BoxParameters.Name) for x in hierarchies])
        for hierarchy in hierarchies:
            hierarchy.x = initial_x_hierarchies
            hierarchy.y = y_hierarchies
            initial_x_hierarchies += GRID_STEP_SIZE * 15
            # Get the TLine of the bushierarchy to be added to the new parentHierarchy
            if hierarchy.uuid in self.graph_manager.line_connection_graph:
                self.graph_manager.line_connection_graph[parent_hierarchy.uuid].extend(
                    self.graph_manager.line_connection_graph.get(hierarchy.uuid)
                )
                # delete the old connection as only the top level information is necessary
                del self.graph_manager.line_connection_graph[hierarchy.uuid]

        # for new_bus_label in filter((lambda x : not x in parent_name), map((lambda x : x.name), bus_labels)):
        #     parent_name += new_bus_label + ", "
        # if len(parent_name) > 0:
        #     parent_name = parent_name[:-2]

        connections_dict = get_connections_dict(bus_labels, subgraph)
        for bus_label in bus_labels:
            bus_label.x = initial_x_bus_labels
            bus_label.y = y_bus_labels

        for component in connecting_components:
            component.x = initial_x_others
            component.y = y_others
            additional_bus_labels = (
                connection_setter.set_on_connection_point(
                    connections_dict, component, self.subsystem
                )
                + additional_bus_labels
            )
            initial_x_others += GRID_STEP_SIZE * 15

        # Set the new name of the parent hierarchy box
        parent_hierarchy.BoxParameters.Name.value = parent_name
        add_elements_to_hierarchy(
            parent_hierarchy,
            bus_labels + hierarchies + connecting_components + additional_bus_labels,
            self.graph_manager,
        )
        update_hierarchy_size(parent_hierarchy)

    def place_last_bus_boxes(self, subsystem: Subsystem) -> None:
        """Places the remaining elements of the draft in the top-level hierarchy
        Remaining components are busLabels to be removed, single and combined bus hierarchies to place
        and the tLine calculation blocks to place"""
        # list of the TLine calculation blocks
        calculation_blocks = []
        # Get all remaining components in the top level hierarchy
        components: list[Component] = subsystem.get_components(False, False)
        for component in components:
            # Remove every bus label as they are unnecessary components
            if component.type == "rtds_sharc_sld_BUSLABEL":
                subsystem.remove_component(component.uuid)
                continue
            if component.type == "lf_rtds_sharc_sld_TL16CAL":
                calculation_blocks.append(component)
        if calculation_blocks:
            calc_hierarchy = create_hierarchy("CalculationBlocks")
            subsystem.add_component(calc_hierarchy)
            add_elements_to_hierarchy(calc_hierarchy, calculation_blocks, self.graph_manager)
            self.remove_from_draft_by_node(calculation_blocks)
        network_solution = rtdsriscNET()
        subsystem.add_component(network_solution)
        # Check if subsystem must be divided, max costs and transmission time need to be added as Parameters.
        # self.checkLoadCosts(30000, subsystem)
        # Place every component in the subystem on the canvas
        self.place_top_level_components(calculation_blocks + [network_solution], subsystem)
        hierarchies = [c for c in subsystem.get_components(False, False) if c.type == "HIERARCHY"]
        self.place_top_level_components(hierarchies + [network_solution], subsystem)
        connection_setter.remove_single_bus_links(subsystem)

    def place_top_level_components(self, components: list[Component], subsystem: Subsystem) -> None:
        """Strategy for placing the component in the highest level of hierarchy on the canvas"""
        x_position = GRID_OFFSET + GRID_STEP_SIZE * 3
        y_position = GRID_OFFSET + GRID_STEP_SIZE * 9
        y_distance_sticky_note = GRID_STEP_SIZE * 3
        step_size = GRID_STEP_SIZE * 9
        bus_box_number = 1
        for component in components:
            component.x = x_position
            component.y = y_position
            # Generate sticky note for the Hierarchy names
            if "bus" in component.name.lower():
                note = stickyNote()
                note.HiddenParameters.DESC1.value = (
                    " The above Bus box contains the following Buses: " + component.name
                )

                note.x = x_position
                note.y = y_distance_sticky_note + component.y
                component.BoxParameters.Name.value = "Bus_Box_" + str(bus_box_number)  # type: ignore
                subsystem.add_component(note)
                bus_box_number += 1
            x_position += step_size
            # Begin a new row after reaching a specific x value in the grid
            if x_position > 2000:
                y_position += step_size
                x_position = GRID_OFFSET + GRID_STEP_SIZE * 3

    def remove_from_draft_by_id(self, node_ids: list) -> None:
        """Removes the given Ids from the top level hierarchy"""
        for node in node_ids:
            self.draft.subsystems[0].remove_component(node, False, False)

    def remove_from_draft_by_node(self, nodes: list) -> None:
        """Removes the given nodes from the top level hierarchy"""
        for node in nodes:
            self.draft.subsystems[0].remove_component(node.uuid, False, False)

    def sum_load_costs(self, subsystem: Subsystem) -> int:
        """Sums up the loadCosts of hierarchies in the given subsystem"""
        # components = self.draft.get_components_by_type('HIERARCHY', False)
        components = [c for c in subsystem.get_components(False, False) if c.type == "HIERARCHY"]
        summed_load_units = 0
        for component in components:
            summed_load_units += self.graph_manager.load_unit_costs[component.uuid]
        return summed_load_units

    def check_load_costs(self, max_load: int, subsystem: Subsystem) -> bool:
        """Checks if the sum of load Costs is higher than maxLoad and if calls a method to divide a subsystem"""
        sum_load_costs = self.sum_load_costs(subsystem)
        if sum_load_costs > max_load:
            self.divide_subsystems(sum_load_costs, subsystem)
            return True
        return False

    def divide_subsystems(self, sum_load_costs: int, subsystem: Subsystem) -> None:
        """Divides a single subsystem into two by removing components from the
        old subsystem and adding them to the new one"""
        new_subsystem = self.create_new_subsystem()
        moved_components = self.graph_manager.distribute_load_unit_costs(
            sum_load_costs, subsystem, 0.0005, 10000, self.tli_files
        )
        if moved_components:
            for component in moved_components:
                component_to_add = self.draft.get_by_id(component)
                if component_to_add is None:
                    raise ValueError(
                        f"Component {component} not found in subsystem {subsystem.tab_name}"
                    )
                new_subsystem.add_component(component_to_add)
                subsystem.remove_component(component)
            connection_setter.remove_single_bus_links(subsystem)
            self.place_last_bus_boxes(new_subsystem)
            Logger.log_to_selected(
                f"Subsystem {subsystem.tab_name} was divided into two subsystems ({len(moved_components)} components moved)"
            )
        else:
            # TODO: Option to remove the newly created but empty subsystem
            Logger.log_to_selected("No valid elements were found to move to a new subsystem")

    def create_new_subsystem(self) -> Subsystem:
        """Creates a new subsystem"""
        subsystem_number = len(self.draft.subsystems)
        subsystem = Subsystem(self.draft, subsystem_number)
        subsystem.tab_name = f"Subsystem_{subsystem_number}"
        self.draft.add_subsystem(subsystem)
        return subsystem
