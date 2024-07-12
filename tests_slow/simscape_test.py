import copy
import os
import itertools
import pathlib
from typing import Any
import unittest
import json

import matlab.engine
import networkx as nx
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.subsystem import Subsystem
from epowcore.simscape.simscape_converter import SimscapeConverter
from tests.helpers.gdf_component_creator import GdfTestComponentCreator


PATH = pathlib.Path(__file__).parent.resolve()


# @unittest.skip("tmp")
class SimscapeTest(unittest.TestCase):
    """Tests for the export of gdf models to simulink models."""

    def test_simulink_simple_subsystem(self) -> None:
        """Test that the converter can convert a simple model.
        The model does not make sense at all.
        """
        creator = GdfTestComponentCreator(50.0)
        buses = [creator.create_bus() for _ in range(4)]
        loads = [creator.create_load() for _ in range(3)]
        three_w_g1 = creator.create_3w_transformer("three_w_g1")

        ieeeg1 = [creator.create_ieeeg1() for _ in range(2)]
        creator.create_tline()  # not connected

        two_w_g1 = creator.create_2w_transformer("two_w_g1")
        ieeest1a = creator.create_ieeest1a("ieeest1a")
        ieeepss1a = creator.create_ieeepss1a("ieeepss1a")

        core_model = creator.core_model

        core_model.add_connection(buses[0], buses[1])
        core_model.add_connection(two_w_g1, loads[1])

        core_model.add_connection(ieeeg1[1], ieeeg1[0], ["In", "Out"], ["Pm", "m"])
        core_model.add_connection(ieeeg1[0], ieeepss1a, "Efd", "In")
        core_model.add_connection(three_w_g1, loads[2], "LV")
        core_model.add_connection(three_w_g1, loads[1], "MV")
        core_model.add_connection(three_w_g1, loads[0], "HV")

        # creating this subsystem triggers the usage of the controller template
        subsystem = Subsystem.from_components(core_model, [ieeeg1[0], ieeest1a, ieeepss1a])
        Subsystem.from_components(core_model, [buses[3]])

        converter = SimscapeConverter()
        converter.from_gdf(core_model, "model_name")
        eng = converter.eng

        graph = _get_graph(eng, "model_name")

        self.assertEqual(len(graph.nodes), 16)
        self.assertEqual(len(graph.edges), 10)

        graph_subsystem = _get_graph(eng, f"model_name/{subsystem.name}")

        self.assertEqual(len(graph_subsystem.nodes), 12)
        self.assertEqual(len(graph_subsystem.edges), 14)

        block_list = eng.getfullname(eng.Simulink.findBlocks("model_name"))
        if not isinstance(block_list, list):
            raise ValueError("Failed to get block list")

        self.assertTrue(
            "model_name/three_w_g1" in _get_neighbors(eng, f"model_name/{loads[0].name}")
        )
        self.assertTrue(
            "model_name/VIM bus1" in _get_neighbors(eng, f"model_name/{buses[0].name}")
        )
        self.assertTrue(
            "model_name/VIM bus2" in _get_neighbors(eng, f"model_name/{buses[1].name}")
        )
        self.assertTrue(
            f"model_name/{ieeeg1[1].name}" in _get_neighbors(eng, f"model_name/{subsystem.name}")
        )
        self.assertEqual(len(_get_points_from_block(eng, f"model_name/{ieeeg1[1].name}")), 2)

        self.assertEqual(len(block_list), 60)
        self.assertEqual(len(list(filter((lambda x: x.count("/") == 1), block_list))), 16)

        self.assertEqual(len(list(filter((lambda x: f"/{subsystem.name}/" in x), block_list))), 42)

        self.assertEqual(
            eng.get_param(f"model_name/{subsystem.name}/Vref", "Value"),
            "1.025",
        )
        self.assertEqual(eng.get_param(f"model_name/{subsystem.name}/Pref", "Value"), "1.2452")
        eng.quit()

    # @unittest.skip("tmp")
    def test_ieee39_export(self) -> None:
        """Tests the export of the IEEE39 model."""
        with open(
            "./tests/models/gdf/IEEE39_gdf.json", "r", encoding="utf8"
        ) as json_file:
            core_model = CoreModel.import_dict(json.loads(json_file.read()))
            sim_conv = SimscapeConverter()
            sim_conv.from_gdf(core_model, "IEEE39")
            graph = _get_graph(sim_conv.eng, "IEEE39")
            self.assertEqual(len(graph.nodes), 164)
            self.assertEqual(len(graph.edges), 313)
            sim_conv.eng.quit()

    # @unittest.skip("tmp")
    def test_nested_templates(self) -> None:
        """Tests the insertion of templates with variant subsystems."""
        creator = GdfTestComponentCreator(50.0)
        gen_1 = creator.create_synchronous_machine()
        ieeest1a = creator.create_ieeest1a()
        ieeeg1 = creator.create_ieeeg1()

        ds_without_pss = copy.deepcopy(creator.core_model)
        ieeepss1a = creator.create_ieeepss1a()
        ds_with_pss = creator.core_model
        for core_model in (ds_with_pss, ds_without_pss):
            core_model.add_connection(ieeeg1, gen_1, "Out", "Pm")
            core_model.add_connection(gen_1, ieeest1a, "m", "m")
        ds_with_pss.add_component(ieeepss1a)
        ds_with_pss.add_connection(ieeepss1a, gen_1, "Out", "Vf")
        converter = SimscapeConverter()
        converter.from_gdf(ds_with_pss, "with_pss")
        converter.from_gdf(ds_without_pss, "without_pss")
        eng = converter.eng

        self.assertEqual(
            eng.get_param(f"with_pss/{ieeeg1.name}/PSS", "LabelModeActiveChoice"),
            "pss1a",
        )
        self.assertEqual(
            eng.get_param(f"without_pss/{ieeeg1.name}/PSS", "LabelModeActiveChoice"),
            "none",
        )
        eng.quit()

    # @unittest.skip("tmp")
    def test_subsystem_group_rules(self) -> None:
        """Test the application of subsystem group rules and the creation of subsystems."""
        creator = GdfTestComponentCreator(50.0)
        ieeeg1 = creator.create_ieeeg1("ieeeg1")
        ieeest1a = creator.create_ieeest1a("ieeest1a")
        ieeepss1a = creator.create_ieeepss1a("ieeepss1a")
        buses = [creator.create_bus() for _ in range(2)]
        core_model = creator.core_model
        core_model.add_connection(ieeeg1, buses[0])
        core_model.add_connection(ieeepss1a, buses[0])
        core_model.add_connection(ieeeg1, buses[1])
        core_model.add_connection(ieeest1a, buses[1])

        converter = SimscapeConverter()
        converter.from_gdf(core_model, "group_rule")
        eng = converter.eng

        graph = _get_graph(eng, "group_rule")
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 0)

    def tearDown(self) -> None:
        created_models = [
            "model_name.slx",
            "subsystem_test_model.slx",
            "group_rule.slx",
            "with_pss.slx",
            "without_pss.slx",
            "IEEE39.slx",
        ]

        for model in created_models:
            if os.path.exists(model):
                os.remove(model)


def _matlab_points_to_lists(points: matlab.double) -> list:
    """Converts matlab points to a list of lists."""
    out: list[list[tuple[float, float]]] = []
    for p in points:
        if len(p.size) > 1:
            out.append([tuple(float(y) for y in x) for x in p])  # type: ignore
        else:
            out.append([tuple(float(x) for x in p)])  # type: ignore
    return out


def __get_points_from_handles(
    eng: matlab.engine.MatlabEngine, port_name: str, handles: dict
) -> list[tuple[str, list]]:
    points = []
    for handle in handles[port_name]:
        if not (handle == -1.0 or all(x == -1.0 for x in handle)):
            if handle.size[0] > 1 and all((x != -1 for x in handle)):
                p = eng.get_param(handle, "Points")
                points.append((port_name, _matlab_points_to_lists(p)))
            else:
                for h in handle:
                    if h != -1.0:
                        p = eng.get_param(h, "Points")
                        points.append((port_name, _matlab_points_to_lists(p)))
    return points


def _get_points_from_block(eng: matlab.engine.MatlabEngine, block_name: str) -> list:
    """Returns a list of (port_name, points) tuples for all ports of a given block."""
    points: list = []
    line_handles = eng.get_param(block_name, "LineHandles")
    if not isinstance(line_handles, dict):
        raise ValueError("Failed to get line handles")
    for port_name in ["Outport", "Inport", "LConn", "RConn"]:
        if (
            line_handles[port_name] != -1.0
            if isinstance(line_handles[port_name], float)
            else not all(map((lambda x: x == -1.0), line_handles[port_name]))
        ):
            if (
                isinstance(line_handles[port_name], matlab.double)
                and len(line_handles[port_name]) > 0
            ):
                points.extend(__get_points_from_handles(eng, port_name, line_handles))
            else:
                handle = line_handles[port_name]

                if (
                    handle == -1.0
                    if isinstance(handle, float)
                    else all(map((lambda x: x == -1.0), handle))
                ):
                    continue
                p = eng.get_param(handle, "Points")
                if not isinstance(p, (list, matlab.double)):
                    raise ValueError("Failed to get points")
                points.append((port_name, _matlab_points_to_lists(p)))
    return points


def _get_graph(eng: matlab.engine.MatlabEngine, model_name: str) -> nx.Graph:
    """Generate a graph of the connections in a layer of the
    simulink model by comparing the end points of the lines.

    :param model_name: The name of the model to generate the graph for.
    :type model_name: str
    """
    graph = nx.Graph()
    block_list = eng.getfullname(eng.Simulink.findBlocks(model_name))
    if not isinstance(block_list, (list, str)):
        raise ValueError("Failed to get block list")
    if isinstance(block_list, str):
        block_list = [block_list]
    pos_dict: dict = {}
    for block_name in block_list:
        if not "/" in block_name[len(model_name) + 2 :]:
            graph.add_node(block_name)
        points = _get_points_from_block(eng, block_name)
        for port_name, ps in points:
            for i, p in enumerate(ps):
                for x, y in p:
                    _add_to_dict_list(pos_dict, (x, y), (block_name, port_name, i))
    for values in pos_dict.values():
        for (block_name, port_name, _), (
            block_name2,
            port_name2,
            _,
        ) in itertools.product(values, values):
            if (
                block_name != block_name2
                and not "/" in block_name[len(model_name) + 2 :]
                and not "/" in block_name2[len(model_name) + 2 :]
            ):
                graph.add_edge(block_name, block_name2)
                graph.edges[block_name, block_name2].update(
                    {
                        block_name: port_name,
                        block_name2: port_name2,
                    }
                )

    return graph


def _filter_handles(handles: matlab.double | float) -> matlab.double | float | list:
    if isinstance(handles, float):
        return handles
    if len(handles) == 0:  # type: ignore
        return -1.0
    handle_list: list[float] = handles if handles.size[1] < 2 else [a for b in handles for a in b]  # type: ignore
    if any(x == -1.0 for x in handle_list):
        return [h for h in handle_list if h != -1.0]
    return handles


def _get_neighbors(eng: matlab.engine.MatlabEngine, block_name: str) -> list:
    """Returns the full name for all blocks connected to a given block.
    !!!Can not recognize blocks connected via bus with more than two connections!!!
    """
    neighbors = []
    line_handles = eng.get_param(block_name, "LineHandles")
    if not isinstance(line_handles, dict):
        raise ValueError("Failed to get line handles")
    for port_name in ["Outport", "Inport", "LConn", "RConn"]:
        handles = _filter_handles(line_handles[port_name])
        if isinstance(handles, (matlab.double, list)):
            for handle in handles:  # type: ignore
                src = eng.get_param(handle, "SrcBlockHandle")
                dst = eng.get_param(handle, "DstBlockHandle")
                if (isinstance(src, float) and src != -1.0) or not any(
                    map((lambda x: x == -1.0), src)  # type: ignore
                ):
                    neighbors.append(eng.getfullname(src))

                if (isinstance(dst, float) and dst != -1.0) or not any(
                    map((lambda x: x == -1.0), dst)  # type: ignore
                ):
                    neighbors.append(eng.getfullname(dst))

        else:
            if (
                handles == -1.0
                if isinstance(handles, float)
                else any(map((lambda x: x == -1.0), handles))  # type: ignore
            ):
                continue
            src = eng.get_param(handles, "SrcBlockHandle")
            dst = eng.get_param(handles, "DstBlockHandle")
            if not isinstance(src, (float, matlab.double)) or not isinstance(
                dst, (float, matlab.double)
            ):
                raise ValueError("Failed to get src or dst")
            if (
                src != -1.0
                if isinstance(src, float)
                else not any(map((lambda x: x == -1.0), src))  # type: ignore
            ):
                neighbors.append(eng.getfullname(src))
            if (
                dst != -1.0
                if isinstance(dst, float)
                else not any(map((lambda x: x == -1.0), dst))  # type: ignore
            ):
                neighbors.append(eng.getfullname(dst))

    neighbors = _flatten(neighbors)
    neighbors = list(filter((lambda x: x != block_name), neighbors))
    return list(set(neighbors))


def _add_to_dict_list(d: dict, key: Any, value: Any) -> None:
    if key not in d:
        d[key] = [value]
    else:
        d[key].append(value)


def _flatten(l: list | tuple) -> list:
    out = []
    for item in l:
        if isinstance(item, (list, tuple)):
            out.extend(_flatten(item))
        else:
            out.append(item)
    return out


if __name__ == "__main__":
    unittest.main()
