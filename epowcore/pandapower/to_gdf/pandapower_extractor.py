import pandas as pd
import pandapower
import math
from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.gdf.core_model import CoreModel
from epowcore.gdf.external_grid import ExternalGrid, ExternalGridType
from epowcore.gdf.generators.static_generator import StaticGenerator
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.load import Load
from epowcore.generic.configuration import Configuration
from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer
from epowcore.gdf.switch import Switch
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.transformers.three_winding_transformer import (
    ThreeWindingTransformer,
)
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.gdf.extended_ward import ExtendedWard
from epowcore.gdf.impedance import Impedance



class PandapowerExtractor:
    """Extract a pandapower network into a GDF CoreModel."""

    def __init__(self, network: pandapower.pandapowerNet) -> None:
        self.network = network

        self.core_model = CoreModel(
            base_frequency=network.f_hz,
            base_mva=network.sn_mva,
        )
        
        self.uid = 0
        self.bus_map: dict[int, Bus] = {}
        self.line_map: dict[int, TLine] = {}
        self.trafo_map: dict[int, TwoWindingTransformer] = {}

        self._extract_buses()
        self._extract_loads()
        self._extract_external_grids()
        self._extract_static_generators()
        self._extract_synchronous_machines()
        self._extract_lines()
        self._extract_two_winding_transformers()
        self._extract_shunts()
        self._extract_switches()
        self._extract_three_winding_transformers()
        self._extract_extended_wards()
        self._extract_impedances()


    def _get_default(
        self,
        component: str,
        attr: str,
        name: str,
    ) -> float:
        value = Configuration().get_default(
            component,
            attr,
            Platform.PANDAPOWER,
        )

        Logger.log_to_selected(
            f"Using default for {component} '{name}': {attr} = {value}"
        )

        if value is None:
            raise ValueError(
                f"No pandapower default configured for {component}.{attr}"
            )

        return float(value)

    def _extract_buses(self) -> None:
        slack_bus_indices = set(
            self.network.ext_grid["bus"].astype(int).tolist()
        )

        for index, row in self.network.bus.iterrows():
            name = row["name"]
            if name is None:
                name = f"Bus {index}"

            bus_type = BusType.BUSBAR
            if row["type"] == "n":
                bus_type = BusType.JUNCTION

            lf_bus_type = (
                LFBusType.SL
                if int(index) in slack_bus_indices
                else LFBusType.PQ
            )

            bus = Bus(
                uid=self.uid,
                name=str(name),
                nominal_voltage=float(row["vn_kv"]),
                lf_bus_type=lf_bus_type,
                bus_type=bus_type,
            )

            self.core_model.add_component(bus)
            self.bus_map[int(index)] = bus
            self.uid += 1

    def _extract_loads(self) -> None:
        for index, row in self.network.load.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                continue

            name = row["name"]
            if name is None:
                name = f"Load {index}"

            load = Load(
                uid=self.uid,
                name=str(name),
                active_power=float(row["p_mw"]),
                reactive_power=float(row["q_mvar"]),
            )

            self.core_model.add_component(load)
            self.core_model.add_connection(
                load,
                self.bus_map[bus_index],
            )

            self.uid += 1

    def _extract_external_grids(self) -> None:
        for index, row in self.network.ext_grid.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                continue

            name = row["name"]
            if name is None:
                name = f"External Grid {index}"

            external_grid = ExternalGrid(
                uid=self.uid,
                name=str(name),
                u_setp=float(row["vm_pu"]),
                p=0.0,
                q=0.0,
                p_min=(
                    float(row["min_p_mw"])
                    if "min_p_mw" in row
                    and not pd.isna(row["min_p_mw"])
                    else None
                ),
                p_max=(
                    float(row["max_p_mw"])
                    if "max_p_mw" in row
                    and not pd.isna(row["max_p_mw"])
                    else None
                ),
                q_min=(
                    float(row["min_q_mvar"])
                    if "min_q_mvar" in row
                    and not pd.isna(row["min_q_mvar"])
                    else 0.0
                ),
                q_max=(
                    float(row["max_q_mvar"])
                    if "max_q_mvar" in row
                    and not pd.isna(row["max_q_mvar"])
                    else 0.0
                ),
                bus_type=ExternalGridType.SL,
            )

            self.core_model.add_component(external_grid)

            bus = self.bus_map[bus_index]

            self.core_model.add_connection(
                external_grid,
                bus,
            )

            self.uid += 1

    def _extract_static_generators(self) -> None:
        for index, row in self.network.sgen.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                continue

            name = row["name"]
            if name is None:
                name = f"Static Generator {index}"

            p_mw = float(row["p_mw"])
            q_mvar = float(row["q_mvar"])

            static_generator = StaticGenerator(
                uid=self.uid,
                name=str(name),
                rated_apparent_power=(
                    float(row["sn_mva"])
                    if "sn_mva" in row
                    and not pd.isna(row["sn_mva"])
                    else 0.0
                ),
                rated_active_power=p_mw,
                active_power=p_mw,
                reactive_power=q_mvar,
                voltage_set_point=1.0,
                p_min=(
                    float(row["min_p_mw"])
                    if "min_p_mw" in row
                    and not pd.isna(row["min_p_mw"])
                    else 0.0
                ),
                p_max=(
                    float(row["max_p_mw"])
                    if "max_p_mw" in row
                    and not pd.isna(row["max_p_mw"])
                    else p_mw
                ),
                q_min=(
                    float(row["min_q_mvar"])
                    if "min_q_mvar" in row
                    and not pd.isna(row["min_q_mvar"])
                    else 0.0
                ),
                q_max=(
                    float(row["max_q_mvar"])
                    if "max_q_mvar" in row
                    and not pd.isna(row["max_q_mvar"])
                    else q_mvar
                ),
            )

            self.core_model.add_component(static_generator)
            self.core_model.add_connection(
                static_generator,
                self.bus_map[bus_index],
            )

            self.uid += 1

    def _extract_synchronous_machines(self) -> None:
        for index, row in self.network.gen.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                continue

            name = row["name"]
            if name is None:
                name = f"Synchronous Machine {index}"

            bus = self.bus_map[bus_index]
            p_mw = float(row["p_mw"])

            rated_apparent_power = (
                float(row["sn_mva"])
                if "sn_mva" in row
                and not pd.isna(row["sn_mva"])
                else abs(p_mw)
            )

            p_min = (
                float(row["min_p_mw"])
                if "min_p_mw" in row
                and not pd.isna(row["min_p_mw"])
                else 0.0
            )

            p_max = (
                float(row["max_p_mw"])
                if "max_p_mw" in row
                and not pd.isna(row["max_p_mw"])
                else p_mw
            )

            q_min = (
                float(row["min_q_mvar"])
                if "min_q_mvar" in row
                and not pd.isna(row["min_q_mvar"])
                else 0.0
            )

            q_max = (
                float(row["max_q_mvar"])
                if "max_q_mvar" in row
                and not pd.isna(row["max_q_mvar"])
                else 0.0
            )

            synchronous_machine = SynchronousMachine(
                uid=self.uid,
                name=str(name),
                rated_apparent_power=rated_apparent_power,
                rated_active_power=p_mw,
                rated_voltage=bus.nominal_voltage,
                active_power=p_mw,
                reactive_power=0.0,
                voltage_set_point=float(row["vm_pu"]),
                inertia_constant=self._get_default(
                    "SynchronousMachine",
                    "inertia_constant",
                    str(name),
                ),
                zero_sequence_resistance=self._get_default(
                    "SynchronousMachine",
                    "zero_sequence_resistance",
                    str(name),
                ),
                zero_sequence_reactance=self._get_default(
                    "SynchronousMachine",
                    "zero_sequence_reactance",
                    str(name),
                ),
                stator_leakage_reactance=self._get_default(
                    "SynchronousMachine",
                    "stator_leakage_reactance",
                    str(name),
                ),
                stator_resistance=self._get_default(
                    "SynchronousMachine",
                    "stator_resistance",
                    str(name),
                ),
                synchronous_reactance_x=self._get_default(
                    "SynchronousMachine",
                    "synchronous_reactance_x",
                    str(name),
                ),
                transient_reactance_x=self._get_default(
                    "SynchronousMachine",
                    "transient_reactance_x",
                    str(name),
                ),
                subtransient_reactance_x=self._get_default(
                    "SynchronousMachine",
                    "subtransient_reactance_x",
                    str(name),
                ),
                synchronous_reactance_q=self._get_default(
                    "SynchronousMachine",
                    "synchronous_reactance_q",
                    str(name),
                ),
                transient_reactance_q=self._get_default(
                    "SynchronousMachine",
                    "transient_reactance_q",
                    str(name),
                ),
                subtransient_reactance_q=self._get_default(
                    "SynchronousMachine",
                    "subtransient_reactance_q",
                    str(name),
                ),
                p_min=p_min,
                p_max=p_max,
                q_min=q_min,
                q_max=q_max,
                pc1=p_min,
                pc2=p_max,
                qc1_min=q_min,
                qc1_max=q_max,
                qc2_min=q_min,
                qc2_max=q_max,
            )

            self.core_model.add_component(synchronous_machine)
            self.core_model.add_connection(
                synchronous_machine,
                bus,
            )

            self.uid += 1

    def _extract_lines(self) -> None:
        for index, row in self.network.line.iterrows():
            from_bus_index = int(row["from_bus"])
            to_bus_index = int(row["to_bus"])

            if (
                from_bus_index not in self.bus_map
                or to_bus_index not in self.bus_map
            ):
                continue

            name = row["name"]
            if name is None:
                name = f"Line {index}"

            from_bus = self.bus_map[from_bus_index]
            to_bus = self.bus_map[to_bus_index]

            # pandapower stores capacitance in nF/km.
            # GDF stores susceptance in uS/km.
            b1 = (
                2
                * math.pi
                * self.network.f_hz
                * float(row["c_nf_per_km"])
                / 1000
            )

            r0 = (
                float(row["r0_ohm_per_km"])
                if "r0_ohm_per_km" in row
                and not pd.isna(row["r0_ohm_per_km"])
                else None
            )

            x0 = (
                float(row["x0_ohm_per_km"])
                if "x0_ohm_per_km" in row
                and not pd.isna(row["x0_ohm_per_km"])
                else None
            )

            b0 = None
            if (
                "c0_nf_per_km" in row
                and not pd.isna(row["c0_nf_per_km"])
            ):
                b0 = (
                    2
                    * math.pi
                    * self.network.f_hz
                    * float(row["c0_nf_per_km"])
                    / 1000
                )

            rating = (
                math.sqrt(3)
                * from_bus.nominal_voltage
                * float(row["max_i_ka"])
            )

            line = TLine(
                uid=self.uid,
                name=str(name),
                length=float(row["length_km"]),
                r1=float(row["r_ohm_per_km"]),
                x1=float(row["x_ohm_per_km"]),
                b1=b1,
                r0=r0,
                x0=x0,
                b0=b0,
                rating=rating,
                parallel_lines=int(row["parallel"]),
            )

            self.core_model.add_component(line)
            self.line_map[int(index)] = line

            self.core_model.add_connection(
                line,
                from_bus,
                connector_name1="A",
            )

            self.core_model.add_connection(
                line,
                to_bus,
                connector_name1="B",
            )

            self.uid += 1

    def _extract_two_winding_transformers(self) -> None:
        for index, row in self.network.trafo.iterrows():
            hv_bus_index = int(row["hv_bus"])
            lv_bus_index = int(row["lv_bus"])

            if (
                hv_bus_index not in self.bus_map
                or lv_bus_index not in self.bus_map
            ):
                continue

            name = row["name"]
            if name is None:
                name = f"Transformer {index}"

            # pandapower gives short-circuit impedance and resistance in percent.
            r1pu = float(row["vkr_percent"]) / 100
            z1pu = float(row["vk_percent"]) / 100
            x1pu = math.sqrt(max(z1pu**2 - r1pu**2, 0.0))

            shift_degree = float(row["shift_degree"])
            phase_shift_30 = round(shift_degree / 30)

            tap_step_percent = row["tap_step_percent"]
            tap_changer_voltage = (
                float(tap_step_percent) / 100
                if not pd.isna(tap_step_percent)
                else None
            )

            transformer = TwoWindingTransformer(
                uid=self.uid,
                name=str(name),
                rating=float(row["sn_mva"]),
                voltage_hv=float(row["vn_hv_kv"]),
                voltage_lv=float(row["vn_lv_kv"]),
                r1pu=r1pu,
                x1pu=x1pu,
                pfe_kw=float(row["pfe_kw"]),
                no_load_current=float(row["i0_percent"]),
                phase_shift_30=phase_shift_30,
                tap_changer_voltage=tap_changer_voltage,
                tap_min=(
                    int(row["tap_min"])
                    if not pd.isna(row["tap_min"])
                    else None
                ),
                tap_max=(
                    int(row["tap_max"])
                    if not pd.isna(row["tap_max"])
                    else None
                ),
                tap_neutral=(
                    int(row["tap_neutral"])
                    if not pd.isna(row["tap_neutral"])
                    else None
                ),
                tap_initial=(
                    int(row["tap_pos"])
                    if not pd.isna(row["tap_pos"])
                    else None
                ),
            )

            self.core_model.add_component(transformer)
            self.trafo_map[int(index)] = transformer

            self.core_model.add_connection(
                transformer,
                self.bus_map[hv_bus_index],
                connector_name1="HV",
            )

            self.core_model.add_connection(
                transformer,
                self.bus_map[lv_bus_index],
                connector_name1="LV",
            )

            self.uid += 1

    
    def _extract_shunts(self) -> None:
        """Extract pandapower shunts into the GDF CoreModel."""
        for index, row in self.network.shunt.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                raise ValueError(
                    f"Shunt {index} references unknown bus {bus_index}"
                )

            name = row["name"]
            if pd.isna(name):
                name = f"Shunt {index}"

            shunt = Shunt(
                uid=self.uid,
                name=str(name),
                p=float(row["p_mw"]),
                q=float(row["q_mvar"]),
            )

            self.core_model.add_component(shunt)

            self.core_model.add_connection(
                shunt,
                self.bus_map[bus_index],
            )

            self.uid += 1

    
    def _extract_impedances(self) -> None:
        """Extract pandapower series impedances into the GDF CoreModel."""

        for index, row in self.network.impedance.iterrows():
            from_bus_index = int(row["from_bus"])
            to_bus_index = int(row["to_bus"])

            if from_bus_index not in self.bus_map:
                raise ValueError(
                    f"Impedance {index} references unknown "
                    f"from_bus {from_bus_index}"
                )

            if to_bus_index not in self.bus_map:
                raise ValueError(
                    f"Impedance {index} references unknown "
                    f"to_bus {to_bus_index}"
                )

            name = row["name"]
            if pd.isna(name):
                name = f"Impedance {index}"

            impedance = Impedance(
                uid=self.uid,
                name=str(name),
                sn_mva=float(row["sn_mva"]),
                r_pu=float(row["rft_pu"]),
                x_pu=float(row["xft_pu"]),
                r_pu_ba=float(row["rtf_pu"]),
                x_pu_ba=float(row["xtf_pu"]),
            )

            self.core_model.add_component(impedance)

            self.core_model.add_connection(
                impedance,
                self.bus_map[from_bus_index],
                connector_name1="A",
            )

            self.core_model.add_connection(
                impedance,
                self.bus_map[to_bus_index],
                connector_name1="B",
            )

            self.uid += 1


    def _extract_shunts(self) -> None:
        """Extract pandapower shunts into the GDF CoreModel."""
        for index, row in self.network.shunt.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                raise ValueError(
                    f"Shunt {index} references unknown bus {bus_index}"
                )

            name = row["name"]
            if pd.isna(name):
                name = f"Shunt {index}"

            shunt = Shunt(
                uid=self.uid,
                name=str(name),
                p=float(row["p_mw"]),
                q=float(row["q_mvar"]),
            )

            self.core_model.add_component(shunt)

            self.core_model.add_connection(
                shunt,
                self.bus_map[bus_index],
            )

            self.uid += 1

    # NEW: Extended wards
    def _extract_extended_wards(self) -> None:
        """Extract pandapower extended wards into GDF."""

        for index, row in self.network.xward.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                raise ValueError(
                    f"Extended ward {index} references unknown bus {bus_index}"
                )

            name = row["name"]
            if pd.isna(name):
                name = f"XWard {index}"

            xward = ExtendedWard(
                uid=self.uid,
                name=str(name),
                p_load=float(row["ps_mw"]),
                q_load=float(row["qs_mvar"]),
                p_gen=0.0,
                q_gen=0.0,
                p_zload=float(row["pz_mw"]),
                q_zload=float(row["qz_mvar"]),
                u_setp=float(row["vm_pu"]),
                r_ext=float(row["r_ohm"]),
                x_ext=float(row["x_ohm"]),
            )

            self.core_model.add_component(xward)

            self.core_model.add_connection(
                xward,
                self.bus_map[bus_index],
            )

            self.uid += 1

    
    def _extract_three_winding_transformers(self) -> None:
        """Extract pandapower three-winding transformers into GDF."""

        for index, row in self.network.trafo3w.iterrows():
            bus_indices = {
                side: int(row[f"{side}_bus"])
                for side in ("hv", "mv", "lv")
            }

            for side, bus_index in bus_indices.items():
                if bus_index not in self.bus_map:
                    raise ValueError(
                        f"Three-winding transformer {index}: "
                        f"missing {side} bus {bus_index}"
                    )

            def impedance(vk_percent: float, vkr_percent: float):
                r = float(vkr_percent) / 100.0
                z = float(vk_percent) / 100.0
                if z < abs(r):
                    raise ValueError(
                        f"Invalid transformer impedance: "
                        f"vk={vk_percent}, vkr={vkr_percent}"
                    )
                x = math.sqrt(max(z**2 - r**2, 0.0))
                return r, x

            r_hm, x_hm = impedance(
                row["vk_hv_percent"], row["vkr_hv_percent"]
            )
            r_ml, x_ml = impedance(
                row["vk_mv_percent"], row["vkr_mv_percent"]
            )
            r_lh, x_lh = impedance(
                row["vk_lv_percent"], row["vkr_lv_percent"]
            )

            def optional_int(value):
                return None if pd.isna(value) else int(value)

            def optional_float(value):
                return None if pd.isna(value) else float(value)

            name = row["name"]
            if pd.isna(name):
                name = f"Three Winding Transformer {index}"

            transformer = ThreeWindingTransformer(
                uid=self.uid,
                name=str(name),
                rating_hv=float(row["sn_hv_mva"]),
                rating_mv=float(row["sn_mv_mva"]),
                rating_lv=float(row["sn_lv_mva"]),
                voltage_hv=float(row["vn_hv_kv"]),
                voltage_mv=float(row["vn_mv_kv"]),
                voltage_lv=float(row["vn_lv_kv"]),
                r1_hm=r_hm,
                r1_ml=r_ml,
                r1_lh=r_lh,
                x1_hm=x_hm,
                x1_ml=x_ml,
                x1_lh=x_lh,
                pfe_kw=float(row["pfe_kw"]),
                no_load_current=float(row["i0_percent"]),
                connection_type_hv=WindingConfig.YN,
                connection_type_mv=WindingConfig.YN,
                connection_type_lv=WindingConfig.YN,
                phase_shift_30_hv=0,
                phase_shift_30_mv=round(float(row["shift_mv_degree"]) / 30),
                phase_shift_30_lv=round(float(row["shift_lv_degree"]) / 30),
                tap_side=(
                    None if pd.isna(row["tap_side"])
                    else str(row["tap_side"])
                ),
                tap_changer_voltage=(
                    optional_float(row["tap_step_percent"]) / 100.0
                    if not pd.isna(row["tap_step_percent"])
                    else None
                ),
                tap_min=optional_int(row["tap_min"]),
                tap_max=optional_int(row["tap_max"]),
                tap_neutral=optional_int(row["tap_neutral"]),
                tap_initial=optional_int(row["tap_pos"]),
                tap_at_star_point=bool(row["tap_at_star_point"]),
            )

            self.core_model.add_component(transformer)

            for side in ("hv", "mv", "lv"):
                self.core_model.add_connection(
                    transformer,
                    self.bus_map[bus_indices[side]],
                    connector_name1=side.upper(),
                )

            self.uid += 1

    def _extract_switches(self) -> None:
        for index, row in self.network.switch.iterrows():
            bus_index = int(row["bus"])

            if bus_index not in self.bus_map:
                continue

            name = row["name"]
            if name is None:
                name = f"Switch {index}"

            switch_bus = self.bus_map[bus_index]
            element_index = int(row["element"])
            element_type = str(row["et"])

            other_component = None

            if element_type == "b":
                other_component = self.bus_map.get(element_index)
            elif element_type == "l":
                other_component = self.line_map.get(element_index)
            elif element_type == "t":
                other_component = self.trafo_map.get(element_index)

            if other_component is None:
                Logger.log_to_selected(
                    f"Skipping switch '{name}': unsupported or missing "
                    f"element type '{element_type}' with index {element_index}"
                )
                continue

            switch = Switch(
                uid=self.uid,
                name=str(name),
                closed=bool(row["closed"]),
                in_service=(
                    bool(row["in_service"])
                    if "in_service" in row
                    and not pd.isna(row["in_service"])
                    else True
                ),
            )

            self.core_model.add_component(switch)

            self.core_model.add_connection(
                switch,
                switch_bus,
            )

            self.core_model.add_connection(
                switch,
                other_component,
            )

            self.uid += 1

    def get_core_model(self) -> CoreModel:
        return self.core_model
