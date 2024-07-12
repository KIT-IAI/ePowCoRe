from epowcore.gdf.data_structure import DataStructure
from epowcore.gdf.bus import Bus, BusType, LFBusType
from epowcore.gdf.exciters.ieee_st1a import IEEEST1A
from epowcore.gdf.generators.epow_generator import EPowGenerator, EPowGeneratorType
from epowcore.gdf.generators.synchronous_machine import SynchronousMachine
from epowcore.gdf.governors.ieee_g1 import IEEEG1
from epowcore.gdf.load import Load
from epowcore.gdf.power_system_stabilizers.ieee_pss1a import IEEEPSS1A, PSS1AInputSelector
from epowcore.gdf.shunt import Shunt
from epowcore.gdf.tline import TLine
from epowcore.gdf.transformers.three_winding_transformer import ThreeWindingTransformer
from epowcore.gdf.transformers.transformer import WindingConfig
from epowcore.gdf.transformers.two_winding_transformer import TwoWindingTransformer


class GdfTestComponentCreator:
    """Creates GDF component with default values for testing purposes."""

    def __init__(self, base_frequency: float = 100.0) -> None:
        """Inititalize"""
        self.base_frequency = base_frequency
        self.next_uid = 1
        self.data_structure = DataStructure(base_frequency=self.base_frequency)

    def __next_uid(self) -> int:
        """Returns next unique id"""
        uid = self.next_uid
        self.next_uid += 1
        return uid

    def create_bus(self, name: str | None = None) -> Bus:
        uid = self.__next_uid()
        bus = Bus(
            uid,
            f"bus{uid}" if name is None else name,
            lf_bus_type=LFBusType.PQ,
            nominal_voltage=110.0,
            bus_type=BusType.BUSBAR,
        )
        self.data_structure.add_component(bus)
        return bus

    def create_load(self, name: str | None = None) -> Load:
        uid = self.__next_uid()
        load = Load(
            uid,
            f"load{uid}" if name is None else name,
            active_power=1.0,
            reactive_power=1.0,
        )
        self.data_structure.add_component(load)
        return load

    def create_3w_transformer(self, name: str | None = None) -> ThreeWindingTransformer:
        uid = self.__next_uid()
        three_winding_transformer = ThreeWindingTransformer(
            uid,
            f"3WTransformer{uid}" if name is None else name,
            rating_hv=100.0,
            rating_mv=50.0,
            rating_lv=20.0,
            voltage_hv=100.0,
            voltage_mv=50.0,
            voltage_lv=10.0,
            x1_hm=0.5,
            x1_ml=0.5,
            x1_lh=0.5,
            r1_hm=0.5,
            r1_ml=0.5,
            r1_lh=0.5,
            pfe_kw=50,
            no_load_current=0.1,
            connection_type_hv=WindingConfig.YN,
            connection_type_mv=WindingConfig.YN,
            connection_type_lv=WindingConfig.YN,
            phase_shift_30_lv=0,
            phase_shift_30_mv=0,
            phase_shift_30_hv=0,
        )
        self.data_structure.add_component(three_winding_transformer)
        return three_winding_transformer

    def create_2w_transformer(self, name: str | None = None) -> TwoWindingTransformer:
        uid = self.__next_uid()
        two_winding_transformer = TwoWindingTransformer(
            uid,
            f"2WTransformer{uid}" if name is None else name,
            rating=100.0,
            voltage_hv=50.0,
            voltage_lv=100.0,
            r1pu=0.2,
            pfe_kw=0.2,
            no_load_current=0.5,
            x1pu=0.5,
            connection_type_hv=WindingConfig.YN,
            connection_type_lv=WindingConfig.YN,
            tap_changer_voltage=0.5,
            tap_min=0,
            tap_max=2,
            tap_neutral=0,
            tap_initial=1,
            phase_shift_30=0,
        )
        self.data_structure.add_component(two_winding_transformer)
        return two_winding_transformer

    def create_ieeeg1(self, name: str | None = None) -> IEEEG1:
        uid = self.__next_uid()
        ieeeg1 = IEEEG1(
            uid,
            f"ieeeg1_{uid}" if name is None else name,
            K=100.0,
            T1=100.0,
            T2=100.0,
            T3=100.0,
            K1=100.0,
            K2=100.0,
            T5=100.0,
            K3=100.0,
            K4=100.0,
            T6=100.0,
            K5=100.0,
            K6=100.0,
            T4=100.0,
            T7=100.0,
            K7=100.0,
            K8=100.0,
            Uc=100.0,
            Pmin=100.0,
            Uo=100.0,
            Pmax=100.0,
            db=100.0,
            PNhp=100.0,
            PNlp=100.0,
        )
        self.data_structure.add_component(ieeeg1)
        return ieeeg1

    def create_ieeest1a(self, name: str | None = None) -> IEEEST1A:
        uid = self.__next_uid()
        ieeest1a = IEEEST1A(
            uid,
            f"ieeest1a_{uid}" if name is None else name,
            Tr=100,
            Ka=100.0,
            Ta=100.0,
            Tb=100.0,
            Tc=100.0,
            Tb1=100.0,
            Tc1=100.0,
            Kf=100.0,
            Tf=100.0,
            Kc=100.0,
            Klr=100.0,
            Ilr=100.0,
            Vs=100.0,
            Vuel=100.0,
            Vi_min=100.0,
            Va_min=100.0,
            Vr_min=100.0,
            Vi_max=100.0,
            Va_max=200.0,
            Vr_max=200.0,
        )
        self.data_structure.add_component(ieeest1a)
        return ieeest1a

    def create_ieeepss1a(self, name: str | None = None) -> IEEEPSS1A:
        uid = self.__next_uid()
        ieeepss1a = IEEEPSS1A(
            uid,
            f"ieeepss1a_{uid}" if name is None else name,
            Vsi_in=PSS1AInputSelector.P_GEN,
            Ks=100.0,
            A1=100.0,
            A2=100.0,
            T1=100.0,
            T2=100.0,
            T3=100.0,
            T4=100.0,
            T5=100.0,
            T6=100.0,
            Vst_min=100.0,
            Vst_max=200.0,
        )
        self.data_structure.add_component(ieeepss1a)
        return ieeepss1a

    def create_synchronous_machine(self, name: str | None = None) -> SynchronousMachine:
        uid = self.__next_uid()
        sync = SynchronousMachine(
            uid,
            f"sync{uid}" if name is None else name,
            rated_apparent_power=100.0,
            rated_active_power=50.0,
            rated_voltage=10.0,
            active_power=0.5,
            reactive_power=0.5,
            voltage_set_point=0.5,
            inertia_constant=0.5,
            zero_sequence_resistance=1.0,
            zero_sequence_reactance=1.0,
            stator_leakage_reactance=1.0,
            stator_resistance=1.0,
            synchronous_reactance_x=1.0,
            transient_reactance_x=1.0,
            subtransient_reactance_x=1.0,
            synchronous_reactance_q=1.0,
            transient_reactance_q=1.0,
            subtransient_reactance_q=1.0,
            p_min=0.0,
            p_max=50.0,
            q_min=0.0,
            q_max=50.0,
            pc1=0.0,
            pc2=0.0,
            qc1_min=0.0,
            qc1_max=0.0,
            qc2_min=0.0,
            qc2_max=0.0,
        )
        self.data_structure.add_component(sync)
        return sync

    def create_tline(self, name: str | None = None) -> TLine:
        uid = self.__next_uid()
        tline = TLine(
            uid,
            f"tline{uid}" if name is None else name,
            length=100.0,
            r1=100.0,
            x1=100.0,
            b1=100.0,
            r0=100.0,
            x0=100.0,
            b0=0.0,
            rating=90.0,
            parallel_lines=1,
        )
        self.data_structure.add_component(tline)
        return tline

    def create_epow_generator(self, name: str | None = None) -> EPowGenerator:
        uid = self.__next_uid()

        generator = EPowGenerator(
            uid,
            f"epow_generator{uid}" if name is None else name,
            None,
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
            10.0,
            1.0,
            1.0,
            1.0,
            10.0,
            10.0,
            10.0,
            1.0,
            1.0,
            ePowGeneratorType=EPowGeneratorType.GAS,
        )
        self.data_structure.add_component(generator)
        return generator

    def create_shunt(self, name: str | None = None) -> Shunt:
        uid = self.__next_uid()
        shunt = Shunt(uid, f"shunt{uid}" if name is None else name, None, p=10.0, q=10.0)
        self.data_structure.add_component(shunt)
        return shunt
