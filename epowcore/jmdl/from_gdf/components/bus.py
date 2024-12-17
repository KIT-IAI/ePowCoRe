from epowcore.gdf.bus import Bus
from epowcore.jmdl.constants import BUS_CLASS_NAME, GDF_JMDL_BUS_TYPE_DICT
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.jmdl.utils import clean

MIN_VOLTAGE_MAGNITUDE = 0.9
MAX_VOLTAGE_MAGNITUDE = 1.1


def create_bus_block(
    bus: Bus, ports: list[Port], geo_data: Data, append_uid: bool = False
) -> Block:
    return Block(
        name=f"{clean(bus.name)}_{bus.uid}" if append_uid else clean(bus.name),
        block_type="BasicBlock",
        block_class=BUS_CLASS_NAME,
        ports=ports,
        tags=["Bus"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "",
                    DataType.GROUP,
                    get_bus_data(bus),
                    None,
                    None,
                    "EPowBus",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        comment="",
        url="",
        layout=Layout(),
    )


def get_bus_data(bus: Bus) -> list[Data]:
    return [
        Data(
            "Determines which of the bus' electrical quantities are a simulation input and which ones are an output.\nPV:  Bus type for usual Generators. It regulates Voltage V and produces a set amount of Power P.\nPQ:  Bus Type for pure Loads. It defines the real and reactive power demand.\nREF: Also known ad Vδ or Slack Bus. The biggest generator usually has this bus type.\n       It regulates the Voltage and determines the voltage phase angle offset for the simulation.\n       It compensates all power shortcommings and surpluses (which is why it should be the strongest generator)\nISOLATED: All Generators, Branches and Loads are disconnected from the bus and therefore isolated from one another.",
            DataType.ENUM,
            [],
            GDF_JMDL_BUS_TYPE_DICT[bus.lf_bus_type],
            "edu.kit.iai.easimov.modeler.model.matpower.BusType",
            "busType",
        ),
        Data(
            "base voltage of the bus in kV",
            DataType.FLOAT64,
            [],
            bus.nominal_voltage,
            None,
            "baseKV",
        ),
        Data(
            "Voltage Magnitude [p.u.]",
            DataType.FLOAT64,
            [],
            1.0,
            None,
            "VMagnitude",
        ),
        Data("Voltage Angle [rad]", DataType.FLOAT64, [], 0.0, "", "VAngle"),
        Data(
            "Minimum voltage magnitude [p.u.]",
            DataType.FLOAT64,
            [],
            MIN_VOLTAGE_MAGNITUDE,
            None,
            "V_min",
        ),
        Data(
            "Maximum voltage magnitude [p.u.]",
            DataType.FLOAT64,
            [],
            MAX_VOLTAGE_MAGNITUDE,
            None,
            "V_max",
        ),
        Data(
            "area number (positive integer)",
            DataType.INT64,
            [],
            0,
            None,
            "Area",
        ),
        Data("loss zone (positive integer)", DataType.INT64, [], 0, None, "Zone"),
    ]
