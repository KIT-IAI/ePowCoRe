import json
import pathlib

from epowcore.gdf.bus import Bus
from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.exciters.exciter import Exciter
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.governors.governor import Governor
from epowcore.gdf.load import Load
from epowcore.gdf.power_system_stabilizers.power_system_stabilizer import PowerSystemStabilizer
from epowcore.gdf.pv_system import PVSystem
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.voltage_source import VoltageSource


PATH = pathlib.Path(__file__).parent.resolve()


def main():
    model_path = PATH.parent / "output/gdf/IEEE39.json"
    with open(model_path, "r", encoding="utf-8") as file:
        data_str = file.read()
    data = json.loads(data_str)
    model = DataStructure.import_dict(data)

    print("Graph")
    print("=====")
    print(f"Nodes:        {len(model.graph.nodes)}")
    print(f"Edges:        {len(model.graph.edges)}")
    print("")
    print("Components")
    print("==========")
    print(f"Buses:        {len(model.type_list(Bus))}")
    print("---")
    print(f"Lines:        {len(model.type_list(TLine))}")
    print(f"2-Wdg Trafos: {len(model.type_list(TwoWindingTransformer))}")
    print(f"3-Wdg Trafos: {len(model.type_list(ThreeWindingTransformer))}")
    print("---")
    print(f"Loads:        {len(model.type_list(Load))}")
    print(f"Shunts:       {len(model.type_list(Shunt))}")
    print("---")
    print(f"Generators:   {len(model.type_list(SynchronousMachine))}")
    print(f"Governors:    {len(model.type_list(Governor))}")
    print(f"Exciters:     {len(model.type_list(Exciter))}")
    print(f"PSSs:         {len(model.type_list(PowerSystemStabilizer))}")
    print("---")
    print(f"V-Sources:    {len(model.type_list(VoltageSource))}")
    print(f"Static Gen:   {len(model.type_list(StaticGenerator))}")
    print(f"PV systems:   {len(model.type_list(PVSystem))}")


if __name__ == "__main__":
    main()
