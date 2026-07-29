"""File providing the unnittest class to test the loadflow results of the exported
pandapower network against the powerfactory results.
In this test for the IEEE39 network.
"""

import json
import pathlib
import unittest
from typing import ClassVar

import pandapower
import pandas
import pytest
from numpy import int64
from pandapower import pandapowerNet
from pandas import DataFrame
from pypsa import Network
from pytest import approx

from epowcore.gdf.core_model import CoreModel
from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.pypsa.pypsa_convert import PyPSAConverter


@pytest.fixture(
    scope="class",
    params=[
        "gdf/IEEE39_gdf.json",
        "gdf/IEEE9_pf_gdf.json",
    ],
)
def model_subpath(request):
    return request.param


@pytest.fixture(scope="class")
def test_model(model_subpath) -> CoreModel:
    PATH = pathlib.Path(__file__).parent.parent.resolve()
    with open(PATH.parent / f"tests/models/{model_subpath}", "r", encoding="utf-8") as file:
        data_str = file.read()
        data = json.loads(data_str)
        return CoreModel.import_dict(data)


@pytest.mark.usefixtures("test_model")
class TestPyPSAExportIEEE39:
    """Unittest testcase child class to provide a test where the IEEE39 testcase
    is exported to pandapower and the loadflow results from the pandapower conversion
    and the powerfactory veresion are compared.
    """

    PYPSA_PREFIX = "pypsa_"
    PP_PREFIX = "pp_"

    core_model: ClassVar[CoreModel]
    pandapower_model: ClassVar[pandapowerNet]
    deviation: ClassVar[float] = 0.05
    pyPSA_model: ClassVar[Network]

    pandapower_bus_results: ClassVar[DataFrame]
    pyPSA_bus_results: ClassVar[dict[str, DataFrame]]
    pandapower_line_results: ClassVar[DataFrame]
    pyPSA_line_results: ClassVar[dict[str, DataFrame]]
    pandapower_gen_results: ClassVar[DataFrame]
    pyPSA_gen_results: ClassVar[dict[str, DataFrame]]

    @classmethod
    @pytest.fixture(autouse=True)
    def prepare_model_data(cls, test_model) -> None:
        cls.core_model = test_model

        pp_converter = PandapowerConverter()
        cls.pandapower_model = pp_converter.from_gdf(
            core_model=cls.core_model, name="IEEE39", log_path=None
        ).network
        pandapower.runpp(net=cls.pandapower_model, numba=False)

        pyPSA_converter = PyPSAConverter()
        cls.pyPSA_model = pyPSA_converter.from_gdf(
            core_model=cls.core_model, name="IEEE39", log_path=None
        )
        cls.pyPSA_model.lpf()
        cls.pyPSA_model.pf(use_seed=True)

        cls.pandapower_bus_results = cls.pandapower_model["res_bus"]
        cls.pyPSA_bus_results = cls.pyPSA_model.components.buses.dynamic

        cls.pandapower_line_results = cls.pandapower_model["res_line"]
        cls.pyPSA_line_results = cls.pyPSA_model.components.lines.dynamic

        cls.pandapower_gen_results = cls.pandapower_model["res_gen"]
        cls.pyPSA_gen_results = cls.pyPSA_model.components.generators.dynamic

    def test_model_consistency(self) -> None:
        self.pyPSA_model.consistency_check(strict="all")

    def convert_pypsa_data(self, data: dict[str, DataFrame]) -> DataFrame:
        result_table: DataFrame
        for index, (key, table) in enumerate(data.items()):
            table = table.transpose()
            table = table.rename(columns={"now": key})
            table.columns.name = None

            if index == 0:
                result_table = table
            else:
                result_table = pandas.concat([result_table, table], axis=1)
        # change dtype of index
        result_table.index = result_table.index.map(int64)

        # change name of index
        result_table = result_table.rename_axis(index={"Bus": None})

        return result_table

    def test_bus_pf_data(self) -> None:
        """Test to check the bus result values of the loadflow"""

        new_table = self.convert_pypsa_data(self.pyPSA_bus_results)

        new_table = new_table.rename(columns=lambda a: self.PYPSA_PREFIX + str(a))
        self.pandapower_bus_results = self.pandapower_bus_results.rename(
            columns=lambda a: self.PP_PREFIX + str(a)
        )

        pf_data = self.pandapower_bus_results.merge(
            new_table,
            left_index=True,
            right_index=True,
        )

        for index, row in pf_data.iterrows():
            pp_value = row[self.PP_PREFIX + "vm_pu"]
            pypsa_value = row[self.PYPSA_PREFIX + "v_mag_pu"]
            assert pp_value == approx(pypsa_value, abs(pp_value * self.deviation)), (
                f"Voltage magnitue of bus {index} uid is deviating by more then "
                + f"{self.deviation*100} percent ({(1-(pypsa_value/pp_value))*100}%)."
            )

    def test_line_pf_data(self) -> None:
        """Test to check the line result values of the loadflow"""
        new_table = self.convert_pypsa_data(self.pyPSA_line_results)

        new_table = new_table.rename(columns=lambda a: self.PYPSA_PREFIX + str(a))
        self.pandapower_line_results = self.pandapower_bus_results.rename(
            columns=lambda a: self.PP_PREFIX + str(a)
        )

        pf_data = self.pandapower_line_results.merge(
            new_table,
            left_index=True,
            right_index=True,
        )
        for index, row in pf_data.iterrows():
            assert row[self.PP_PREFIX + "p_from_mw"] == approx(
                row[self.PYPSA_PREFIX + "p0"],
                abs(row[self.PP_PREFIX + "p_from_mw"] * self.deviation),
            ), (
                f"p0 of line {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'p0']/row[self.PP_PREFIX + 'p_from_mw']))*100}%)."
            )
            assert row[self.PP_PREFIX + "p_to_mw"] == approx(
                row[self.PYPSA_PREFIX + "p1"], abs(row[self.PP_PREFIX + "p_to_mw"] * self.deviation)
            ), (
                f"p1 of line {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'p1']/row[self.PP_PREFIX + 'p_to_mw']))*100}%)."
            )
            assert row[self.PP_PREFIX + "q_from_mvar"] == approx(
                row[self.PYPSA_PREFIX + "q0"],
                abs(row[self.PP_PREFIX + "q_from_mvar"] * self.deviation),
            ), (
                f"q0 of line {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'q0']/row[self.PP_PREFIX + 'q_from_mvar']))*100}%)."
            )
            assert row[self.PP_PREFIX + "q_to_mvar"] == approx(
                row[self.PYPSA_PREFIX + "q1"],
                abs(row[self.PP_PREFIX + "q_to_mvar"] * self.deviation),
            ), (
                f"q1 of line {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'q1']/row[self.PP_PREFIX + 'q_to_mvar']))*100}%)."
            )

    def test_gen_pf_data(self) -> None:
        """Test to check the gen result values of the loadflow"""
        new_table = self.convert_pypsa_data(self.pyPSA_gen_results)

        new_table = new_table.rename(columns=lambda a: self.PYPSA_PREFIX + str(a))
        self.pandapower_gen_results = self.pandapower_bus_results.rename(
            columns=lambda a: self.PP_PREFIX + str(a)
        )

        pf_data = self.pandapower_gen_results.merge(
            new_table,
            left_index=True,
            right_index=True,
        )

        for index, row in pf_data.iterrows():
            assert row[self.PP_PREFIX + "p_mw"] == approx(
                row[self.PYPSA_PREFIX + "p"], abs(row[self.PP_PREFIX + "p_mw"] * self.deviation)
            ), (
                f"p of gen {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'p']/row[self.PP_PREFIX + 'p_mw']))*100}%)."
            )
            assert row[self.PP_PREFIX + "q_mvar"] == approx(
                row[self.PYPSA_PREFIX + "q"], abs(row[self.PP_PREFIX + "q_mvar"] * self.deviation)
            ), (
                f"q of gen {index} is deviating by more then {self.deviation*100} percent"
                + f" ({(1-(row[self.PYPSA_PREFIX + 'q']/row[self.PP_PREFIX + 'q_mvar']))*100}%)."
            )
