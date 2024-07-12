from epowcore.gdf.generators.epow_generator import (
    EPowGeneratorCostModel,
    EPowGeneratorType,
)
from epowcore.gdf.voltage_source import VoltageSource
from epowcore.jmdl.constants import GENERATOR_CLASS_NAME
from epowcore.jmdl.utils import clean
from epowcore.jmdl.jmdl_model import Block, Data, DataType, Layout, Port
from epowcore.generic.configuration import Configuration


def create_vsource_block(
    vsource: VoltageSource, ports: list[Port], geo_data: Data, append_uid: bool = False
) -> Block:
    return Block(
        name=f"{clean(vsource.name)}_{vsource.uid}"
        if append_uid
        else clean(vsource.name),
        block_type="BasicBlock",
        block_class=GENERATOR_CLASS_NAME,
        ports=ports,
        comment="",
        url="",
        tags=["Generator"],
        data=Data(
            "",
            DataType.GROUP,
            [
                Data(
                    "",
                    DataType.GROUP,
                    get_vsource_data(vsource),
                    None,
                    None,
                    "EPowGenerator",
                ),
                geo_data,
            ],
            None,
            None,
            "data",
        ),
        layout=Layout(),
    )


def get_vsource_data(vsource: VoltageSource) -> list[Data]:
    return [
        Data(
            "voltage magnitude setpoint.",
            DataType.FLOAT64,
            [],
            vsource.u_setp,
            None,
            "V",
        ),
        Data(
            "Real Power Output [MW]",
            DataType.FLOAT64,
            [],
            0.0,
            None,
            "P",
        ),
        Data(
            "Reactive Power Output [MVar]",
            DataType.FLOAT64,
            [],
            0.0,
            None,
            "Q",
        ),
        Data(
            "Type of the Generator",
            DataType.ENUM,
            [],
            EPowGeneratorType.OTHERS.value,
            "edu.kit.iai.easimov.modeler.util.GeneratorType",
            "type",
        ),
        Data("inService", DataType.BOOL, [], True, None, "inService"),
        Data(
            "Minimum Real Power Output [MW]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.PMin"),
            None,
            "Pmin",
        ),
        Data(
            "Maximum Real Power Output [MW]",
            DataType.FLOAT64,
            [],
            None,
            "Pmax",
        ),
        Data(
            "Minimum Reactive Power Output [MVar]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QMin"),
            None,
            "Qmin",
        ),
        Data(
            "Maximum Reactive Power Output [MVar]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QMax"),
            None,
            "Qmax",
        ),
        Data(
            "Total MVA base of the machine, defaults to baseMVA of the network",
            DataType.FLOAT64,
            [],
            1.0,
            None,
            "baseMVA",
        ),
        Data(
            "Lower real power output of PQ capability curve [MV]",
            DataType.FLOAT64,
            [],
            0.0,
            None,
            "PC1",
        ),
        Data(
            "Upper real power output of PQ capability curve [MV]",
            DataType.FLOAT64,
            [],
            0.0,
            None,
            "PC2",
        ),
        Data(
            "Minimum reactive power output at PC1 [MV]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QC1Min"),
            None,
            "QC1Min",
        ),
        Data(
            "Maximum reactive power output at PC1 [MV]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QC1Max"),
            None,
            "QC1Max",
        ),
        Data(
            "Minimum reactive power output at PC2 [MV]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QC2Min"),
            None,
            "QC2Min",
        ),
        Data(
            "Maximum reactive power output at PC2 [MV]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.QC2Max"),
            None,
            "QC2Max",
        ),
        Data(
            "Ramp rate for 10 minute reserves [MW]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.ramp10"),
            None,
            "ramp10",
        ),
        Data(
            "Ramp rate for 30 minute reserves [MW]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.ramp30"),
            None,
            "ramp30",
        ),
        Data(
            "Ramp rate for reactive power (2 sec time scale) [MVAr/min]",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.rampQ"),
            None,
            "rampQ",
        ),
        Data(
            "Area participation factor",
            DataType.FLOAT64,
            [],
            0.0,
            None,
            "APF",
        ),
        Data(
            "None (0), Piecewise linear (1), Polynomial (2)",
            DataType.ENUM,
            [],
            EPowGeneratorCostModel.POLYNOMIAL.value,
            "edu.kit.iai.easimov.modeler.util.GeneratorCostModel",
            "costModel",
        ),
        Data(
            "Generator startup cost in US dollars.",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.costStartUp"),
            None,
            "costStartUp",
        ),
        Data(
            "Generator shutdown cost in US dollars.",
            DataType.FLOAT64,
            [],
            Configuration().get("JMDL.VoltageSource.costShutDown"),
            None,
            "costShutDown",
        ),
        Data(
            "Number of cost parameters",
            DataType.INT64,
            [],
            3,
            None,
            "costNumParameters",
        ),
        Data(
            "Parameters defining total cost function f(p). Units of f and p are $/hr and MW (or MVAr), Piecewise Linear: p0,f0,p1,f1,...,pn,fn, where p0 < p1 < ... < pn. The cost f(p) is defined by the coordinates (p0,f0),(p1,f1),...,(pn,fn). Polymomial: cn, ..., c1, c0. With n+1 coefficients of n-th order polynomial cost, starting with highest order, where cost is f(p) = cnp^n + + c1p + c0",
            DataType.STRING,
            [],
            "0 1 0",
            None,
            "costParameters",
        ),
    ]
