"""File providing the unnittest class to test the loadflow results of the exported 
pandapower network against the powerfactory results.
In this test for the IEEE39 network.
"""

import json
import pathlib
import unittest

import pandas
import pandapower

from epowcore.generic.logger import Logger
from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.gdf.core_model import CoreModel


class PandapowerExportIEEE39Test(unittest.TestCase):
    """Unittest testcase child class to provide a test where the IEEE39 testcase
    is exported to pandapower and the loadflow results from the pandapower conversion
    and the powerfactory veresion are compared.
    """

    @classmethod
    def setUpClass(cls):
        cls.percent_deviation = 0.05

        PATH = pathlib.Path(__file__).parent.parent.resolve()
        with open(PATH.parent / "tests/models/gdf/IEEE39_gdf.json", "r", encoding="utf-8") as file:
            data_str = file.read()
            data = json.loads(data_str)
            cls.core_model = CoreModel.import_dict(data)

        cls.pf_data = {}
        cls.pf_data["Bus"] = pandas.read_csv(
            filepath_or_buffer=PATH.parent / "tests/data/loadflow/pf_IEEE39/Bus.csv",
            index_col=0,
            sep=";",
        )
        cls.pf_data["SynchronousMachine"] = pandas.read_csv(
            filepath_or_buffer=PATH.parent / "tests/data/loadflow/pf_IEEE39/SynchronousMachine.csv",
            index_col=0,
            sep=";",
        )
        cls.pf_data["TLine"] = pandas.read_csv(
            filepath_or_buffer=PATH.parent / "tests/data/loadflow/pf_IEEE39/TLine.csv",
            index_col=0,
            sep=";",
        )

        converter = PandapowerConverter()
        cls.pandapower_model = converter.from_gdf(
            core_model=cls.core_model, name="IEEE39", log_path=None
        ).network
        pandapower.runpp(net=cls.pandapower_model)

    def test_bus_pf_data(self):
        """Test to check the bus result values of the loadflow"""
        self.pandapower_model["res_bus"] = pandas.concat(
            [self.pandapower_model["res_bus"], self.pandapower_model["bus"]["name"]], axis=1
        )
        for _, row in self.pf_data["Bus"].iterrows():
            try:
                pandapower_row = self.pandapower_model["res_bus"].loc[
                    self.pandapower_model["res_bus"]["name"] == row["name"]
                ]
            except KeyError:
                Logger.log_to_selected(
                    f"GDF Bus: {row['name']} wasn't found in pandapower converted model."
                )
            self.assertAlmostEqual(
                row["voltage_magnitude[pu]"],
                pandapower_row.iloc[0]["vm_pu"],
                delta=abs(row["voltage_magnitude[pu]"] * self.percent_deviation),
                msg=f"voltage_magnitude[pu] of {row['name']} is deviating by more then 5 percent.",
            )

    def test_line_pf_data(self):
        """Test to check the line result values of the loadflow"""
        self.pandapower_model["res_line"] = pandas.concat(
            [self.pandapower_model["res_line"], self.pandapower_model["line"]["name"]], axis=1
        )
        for _, row in self.pf_data["TLine"].iterrows():
            try:
                pandapower_row = self.pandapower_model["res_line"].loc[
                    self.pandapower_model["res_line"]["name"] == row["name"]
                ]
            except KeyError:
                Logger.log_to_selected(
                    f"GDF TLine: {row['name']} wasn't found in pandapower converted model."
                )
            self.assertAlmostEqual(
                row["p_from[MW]"],
                pandapower_row.iloc[0]["p_from_mw"],
                delta=abs(row["p_from[MW]"] * self.percent_deviation),
                msg=f"p_from[MW] of {row['name']} is deviating by more then 5 percent.",
            )
            self.assertAlmostEqual(
                row["p_to[MW]"],
                pandapower_row.iloc[0]["p_to_mw"],
                delta=abs(row["p_to[MW]"] * self.percent_deviation),
                msg=f"p_to[MW] of {row['name']} is deviating by more then 5 percent.",
            )
            self.assertAlmostEqual(
                row["q_from[MVar]"],
                pandapower_row.iloc[0]["q_from_mvar"],
                delta=abs(row["q_from[MVar]"] * self.percent_deviation),
                msg=f"q_from[MVar] of {row['name']} is deviating by more then 5 percent.",
            )
            self.assertAlmostEqual(
                row["q_to[MVar]"],
                pandapower_row.iloc[0]["q_to_mvar"],
                delta=abs(row["q_to[MVar]"] * self.percent_deviation),
                msg=f"q_to[MVar] of {row['name']} is deviating by more then 5 percent.",
            )

    def test_gen_pf_data(self):
        """Test to check the gen result values of the loadflow"""
        self.pandapower_model["res_gen"] = pandas.concat(
            [self.pandapower_model["res_gen"], self.pandapower_model["gen"]["name"]], axis=1
        )
        for _, row in self.pf_data["SynchronousMachine"].iterrows():
            try:
                pandapower_row = self.pandapower_model["res_gen"].loc[
                    self.pandapower_model["res_gen"]["name"] == row["name"]
                ]
            except KeyError:
                Logger.log_to_selected(
                    f"GDF SynchronousMachine: {row['name']} wasn't found in pandapower converted model."
                )

            self.assertAlmostEqual(
                row["p_from[MW]"],
                pandapower_row.iloc[0]["p_mw"],
                delta=abs(row["p_from[MW]"] * self.percent_deviation),
                msg=f"p_from[MW] of {row['name']} is deviating by more then 5 percent.",
            )
            self.assertAlmostEqual(
                row["q_from[MVar]"],
                pandapower_row.iloc[0]["q_mvar"],
                delta=abs(row["q_from[MVar]"] * self.percent_deviation),
                msg=f"q_from[MVar] of {row['name']} is deviating by more then 5 percent.",
            )
