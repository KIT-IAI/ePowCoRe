import unittest

from helpers.gdf_component_creator import GdfTestComponentCreator
from pyapi_rts.generated.BUS import BUS as RSCADBus
from pyapi_rts.generated.HIERARCHY import HIERARCHY as RSCADHierarchy
from pyapi_rts.generated.lfrtdssharcsldMACV31 import lfrtdssharcsldMACV31 as RSCADSynchronousMachine
from pyapi_rts.generated.rtds3P2WTRFdef import rtds3P2WTRFdef as RSCAD2WindingTransformer
from pyapi_rts.generated.rtds3P3WTRFdef import rtds3P3WTRFdef as RSCAD3WindingTransformer
from pyapi_rts.generated.rtdssharcsldBUSLABEL import rtdssharcsldBUSLABEL as RSCADBuslabel

from epowcore.gdf.subsystem import Subsystem
from epowcore.generic.singleton import Singleton
from epowcore.rscad.rscad_converter import RscadConverter


class RSCADExportTest(unittest.TestCase):
    """Tests the export from GDF to RSCAD."""

    def setUp(self) -> None:
        Singleton._instances = {}

    def test_basic(self) -> None:
        """Tests the export of a simple system."""
        creator = GdfTestComponentCreator()
        buses = [creator.create_bus() for _ in range(5)]
        trafo1 = creator.create_3w_transformer()
        trafo2 = creator.create_2w_transformer()
        sync1 = creator.create_synchronous_machine()

        core_model = creator.core_model
        core_model.add_connection(buses[2], buses[4])

        subsystem = Subsystem.from_components(core_model, [buses[4]])

        # core_model.add_component(sync1)
        core_model.add_connection(buses[0], trafo1, "", "LV")
        core_model.add_connection(buses[1], trafo1, "", "MV")
        core_model.add_connection(buses[0], sync1, "", "")
        core_model.add_connection(trafo1, trafo2, "HV", "HV")

        converter = RscadConverter()
        rscad_model = converter.from_gdf(core_model, "test")
        draft = rscad_model.draft
        draft.write_file("tests/out/test1.dfx")
        components = draft.get_components()
        three_winding = [x for x in components if isinstance(x, RSCAD3WindingTransformer)][0]

        connections = draft.get_graph()
        three_wt_neighbours = list(connections.neighbors(three_winding.uuid))
        self.assertEqual(len(three_wt_neighbours), 3)
        for neighbour in three_wt_neighbours:
            self.assertTrue(
                isinstance(draft.get_by_id(neighbour), RSCADBuslabel)
            )  # All connections are buses

        two_winding = [x for x in components if isinstance(x, RSCAD2WindingTransformer)][0]
        two_wt_bus = draft.get_by_id(next((connections.neighbors(two_winding.uuid))))

        # Two winding trafo is connected to three winding trafo
        self.assertTrue(
            two_wt_bus.name  # type: ignore
            in map((lambda x: draft.get_by_id(x).name), three_wt_neighbours)  # type: ignore
        )
        sync_rscad = [x for x in components if isinstance(x, RSCADSynchronousMachine)][0]
        sync_connected = list(map(draft.get_by_id, connections.neighbors(sync_rscad.uuid)))
        self.assertEqual(len([x for x in sync_connected if isinstance(x, RSCADBus)]), 1)

        # Check the naming of the hierarchies
        top_level_hierarchy = [
            x
            for x in draft.subsystems[0].get_components(recursive=False)
            if isinstance(x, RSCADHierarchy)
        ][0]
        self.assertEqual(top_level_hierarchy.name, "Bus_Box_1")
        self.assertEqual(
            next(
                filter(
                    lambda x: isinstance(x, RSCADHierarchy),
                    top_level_hierarchy.get_components(recursive=False),  # type: ignore
                ),
                None,
            ).name,  # type: ignore
            "bus1",
        )
        draft.write_file("tests/out/test1.dfx")


if __name__ == "__main__":
    unittest.main()
