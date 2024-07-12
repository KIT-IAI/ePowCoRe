from typing import Any

import pyapi_rts.generated.rtdsudcDYLOAD as rdyLoad
import pyapi_rts.generated.rtdssharcsldBUSLABEL as rbus
import pyapi_rts.generated.rtdsIEEET1def as rscadIEEET1
import pyapi_rts.generated.rtdsEXST1Adef as rscadIEEEST1A
import pyapi_rts.generated.rtdsIEEEG1def as rscadIEEEG1
import pyapi_rts.generated.rtdsPTIST1def as rscadPTIST1
import pyapi_rts.generated.rtdsPSS1Adef as rscadPSS1A
import pyapi_rts.generated.lfrtdssharcsldTLINE as rscadTLine
import pyapi_rts.generated.lfrtdssharcsldTL16CAL as rscadTLineCalc
import pyapi_rts.generated.enums.EndsrEnumParameter as TLineEnum
from pyapi_rts.generated.rtds3P2WTRFdef import rtds3P2WTRFdef
from pyapi_rts.generated.rtds3P3WTRFdef import rtds3P3WTRFdef
import pyapi_rts.generated.lfrtdssharcsldMACV31 as rscadSynchronousMachineMACV31

from pyapi_rts.generated.rtdsPI123def import rtdsPI123def as PiSection
from pyapi_rts.api.lark.rlc_tline import RLCTLine
from pyapi_rts.generated.enums.Noyes2EnumParameter import Noyes2Enum
from pyapi_rts.generated.enums.RaisttEnumParameter import RaisttEnum
from epowcore.generic.component_graph import ComponentGraph


from epowcore.generic.logger import Logger
from epowcore.gdf import Bus, Load, TLine
from epowcore.gdf.generators import (
    Generator,
    SynchronousMachine,
)
from epowcore.gdf.exciters import IEEET1, IEEEST1A, Exciter
from epowcore.gdf.governors import IEEEG1, Governor
from epowcore.gdf.power_system_stabilizers import (
    PTIST1,
    IEEEPSS1A as PSS1A,
    PowerSystemStabilizer as PSS,
)
from epowcore.gdf.transformers import (
    Transformer,
    ThreeWindingTransformer as Transformer3W,
    TwoWindingTransformer as Transformer2W,
)
from epowcore.generic.configuration import Configuration
from epowcore.rscad.components import *
from epowcore.rscad.components.base_component_builder import RSCADComponentBuilder


TLineElements = tuple[
    rscadTLine.lfrtdssharcsldTLINE,
    rscadTLine.lfrtdssharcsldTLINE,
    rscadTLineCalc.lfrtdssharcsldTL16CAL,
]


class RscadComponentCreator:
    """This is a helper class creating RSCAD Components"""

    def __init__(self, graph: ComponentGraph, base_frequency: float) -> None:
        self.graph = graph
        self.base_frequency = base_frequency

    def create_rscad_bus(self, bus: Bus) -> rbus.rtdssharcsldBUSLABEL:
        """Creates a RSCAD bus from a dataStructure Bus element and sets the available values.
        Also creates a BUS for every connection the bus has plus one additional to connect everything
        """
        return RSCADBus.create(bus, self.base_frequency)

    def create_rscad_dyload(self, load: Load) -> rdyLoad.rtdsudcDYLOAD:
        """Creates a RSCAD dynamic load from a datastructure Load element and sets the available values"""
        edges = self.graph.edges(load)
        # Get nominal Voltage of the bus in the remaining tuple
        vbus = list(edges)[0][1].nominal_voltage  # type: ignore

        return RSCADDyload.create(load, vbus)

    def create_rscad_tline(self, tline: TLine) -> TLineElements:
        """Creates two RSCAD TLines (SE and RE) and a TLine calculation block from a datastructure
        TLine element and sets the available values. Return as a hierarchy box"""
        # Generate sending line
        rs_line_sending = rscadTLine.lfrtdssharcsldTLINE()
        rs_line_sending.CONFIGURATION.Tnam1.value = RSCADComponentBuilder.sanitize_string(
            tline.name
        )
        rs_line_sending.CONFIGURATION.Name.value = (
            RSCADComponentBuilder.sanitize_string(tline.name) + "SE"
        )
        # This should probably be somewhere in the generic data format
        rs_line_sending.CONFIGURATION.numc.value = 3
        rs_line_sending.CONFIGURATION.endsr.value = TLineEnum.EndsrEnum.SENDING

        # Generate receiving line
        rs_line_receiving = rscadTLine.lfrtdssharcsldTLINE()
        rs_line_receiving.CONFIGURATION.Tnam1.value = RSCADComponentBuilder.sanitize_string(
            tline.name
        )

        rs_line_receiving.CONFIGURATION.Name.value = (
            RSCADComponentBuilder.sanitize_string(tline.name) + "RE"
        )

        # This should probably be somewhere in the generic data format
        rs_line_receiving.CONFIGURATION.numc.value = 3
        rs_line_receiving.CONFIGURATION.endsr.value = TLineEnum.EndsrEnum.RECEIVING
        # Generate the Calculation Box
        rs_calc_box = rscadTLineCalc.lfrtdssharcsldTL16CAL()
        rs_calc_box.CONFIGURATION.Name.value = RSCADComponentBuilder.sanitize_string(tline.name)
        rs_calc_box.CONFIGURATION.Dnm1.value = RSCADComponentBuilder.sanitize_string(tline.name)
        rs_calc_box.OPTIONSWHENUSINGBERGERONDATA.alwpi.value = Noyes2Enum.No
        rs_calc_box.OPTIONSWHENUSINGBERGERONDATA.raistt.value = RaisttEnum.RaiseTT
        return (rs_line_sending, rs_line_receiving, rs_calc_box)

    def create_tli_file(self, tline: TLine) -> RLCTLine:
        "Creates a .tli file in RLC format with the given values of tLine"
        tli_file = RLCTLine(RSCADComponentBuilder.sanitize_string(tline.name))
        log_string = f"RLCTLine|{tli_file.name}|"
        tli_file.length = tline.get_fb("length")
        tli_file.frequency = self.base_frequency
        # Set the positive sequence values to their default values if they are 0
        if tline.r1 == 0:
            tli_file.r1 = Configuration().get("RSCAD.TLine.r1_min")
            log_string += f"Positive Sequence Series Resistance: {tli_file.r1}\n"
        else:
            tli_file.r1 = tline.r1
        if tline.x1 == 0:
            tli_file.xind1 = Configuration().get("RSCAD.TLine.x1_min")
            log_string += f"Positive Sequence Series Ind. Reactance: {tli_file.xind1}\n"
        else:
            tli_file.xind1 = tline.x1
        if tline.b1 == 0:
            tli_file.xcap1 = Configuration().get("RSCAD.TLine.xc1_min")
            log_string += f"Positive Sequence Series Shunt Cap. Resistance: {tli_file.xcap1}\n"
        else:
            tli_file.xcap1 = 1 / tline.b1

        # Set zero sequence values to their positive sequence values if they are 0
        if tline.r0 is None or tline.r0 == 0:
            r0 = tline.r0_fb(log=False)
            if r0 == 0:
                tli_file.r0 = Configuration().get("RSCAD.TLine.r0_min")
            else:
                tli_file.r0 = r0
            log_string += f"Zero Sequence Series Resistance: {tli_file.r0}\n"
        else:
            tli_file.r0 = tline.r0

        if tline.x0 is None or tline.x0 == 0:
            x0 = tline.x0_fb(log=False)
            if x0 == 0:
                tli_file.xind0 = Configuration().get("RSCAD.TLine.x0_min")
            else:
                tli_file.xind0 = x0
            log_string += f"Zero Sequence Series Ind. Reactance: {tli_file.xind0}\n"
        else:
            tli_file.xind0 = tline.x0

        if tline.b0 is None or tline.b0 == 0:
            b0 = tline.b0_fb(log=False)
            if b0 == 0:
                tli_file.xcap0 = Configuration().get("RSCAD.TLine.xc0_min")
            else:
                tli_file.xcap0 = 1.0 / b0
            log_string += f"Zero Sequence Series Shunt Cap. Reactance: {tli_file.xcap0}\n"
        else:
            tli_file.xcap0 = 1.0 / tline.b0

        # Only print out logstring if something was changed
        if log_string != f"RLCTLine|{tli_file.name}|":
            Logger.log_to_selected(log_string)
        return tli_file

    def create_pi_from_tline(self, tline: TLine) -> PiSection:
        "Create a Pi component from a line to substitute it"
        pi_section = PiSection()

        pi_section.CONFIGURATION.Name.value = tline.name
        pi_section.PARAMETERS.Rp.value = (
            tline.r1 if tline.r1 > 0 else Configuration().get("RSCAD.PiSection.r1_min")
        )

        pi_section.PARAMETERS.Xp.value = (
            tline.x1 if tline.x1 > 0 else Configuration().get("RSCAD.PiSection.x1_min")
        )

        if tline.r0_fb() > 0:
            pi_section.PARAMETERS.Rz.value = tline.r0_fb()
        else:
            pi_section.PARAMETERS.Rz.value = Configuration().get("RSCAD.PiSection.r0_min")

        if tline.x0_fb() > 0:
            pi_section.PARAMETERS.Xz.value = tline.x0_fb()
        else:
            pi_section.PARAMETERS.Xz.value = Configuration().get("RSCAD.PiSection.x0_min")

        if tline.b1 == 0:
            pi_section.CONFIGURATION.incShuntCaps.value = Noyes2Enum.No
        else:
            pi_section.PARAMETERS.Xcp.value = 1 / tline.b1
            pi_section.PARAMETERS.Xcz.value = 1 / tline.b0_fb()

        return pi_section

    def create_rscad_transformer(
        self, transformer: Transformer
    ) -> rtds3P2WTRFdef | rtds3P3WTRFdef | None:
        """Check which RSCAD transformer should be created"""
        if isinstance(transformer, Transformer2W):
            return RSCAD2WTransformer.create(transformer, self.base_frequency)
        if isinstance(transformer, Transformer3W):
            return RSCAD3WTransformer.create(transformer, self.base_frequency)
        return None

    def create_rscad_generator(
        self, generator: Generator
    ) -> rscadSynchronousMachineMACV31.lfrtdssharcsldMACV31 | None:
        """Check which RSCAD generator should be created"""
        return (
            RSCADSynchronousMachine.create(generator, self.base_frequency)
            if isinstance(generator, SynchronousMachine)
            else None
        )

    def create_rscad_exciter(
        self, exciter: Exciter
    ) -> rscadIEEET1.rtdsIEEET1def | rscadIEEEST1A.rtdsEXST1Adef | None:
        """Check which RSCAD exciter should be created"""
        if isinstance(exciter, IEEET1):
            return self.create_rscad_ieeet1(exciter)
        if isinstance(exciter, IEEEST1A):
            return self.create_rscad_ieeest1a(exciter)
        return None

    def create_rscad_ieeet1(self, exciter: IEEET1) -> rscadIEEET1.rtdsIEEET1def:
        """Creates a RSCAD IEEET1 exciter from a datastructure IEEET1 exciter element and sets the available values"""
        generator = self.try_get_connected_generator(exciter)
        if generator is None:
            raise ValueError("No generator connected to component")
        # Bus is always the second parameter in the tuple
        return RSCADIEEET1.create(exciter, self.base_frequency, generator)

    def create_rscad_ieeest1a(self, exciter: IEEEST1A) -> rscadIEEEST1A.rtdsEXST1Adef:
        """Creates a RSCAD IEEET1 exciter from a datastructure IEEET1 exciter element and sets the available values"""
        # Only Connection is the generator
        generator = self.try_get_connected_generator(exciter)
        if generator is None:
            raise ValueError("No generator connected to component")
        # Bus is always the second parameter in the tuple
        return RSCADIEEEST1A.create(exciter, self.base_frequency, generator)

    def create_rscad_governor(self, governor: Governor) -> rscadIEEEG1.rtdsIEEEG1def | None:
        """Check which RSCAD governor should be created"""
        if isinstance(governor, IEEEG1):
            return self.create_rscad_ieeeg1(governor)
        return None

    def create_rscad_ieeeg1(self, governor: IEEEG1) -> rscadIEEEG1.rtdsIEEEG1def:
        """Creates a RSCAD IEEEG1 governor from a datastructure IEEEG1 governor element and sets the available values"""
        # Only Connection is the generator
        generator = self.try_get_connected_generator(governor)
        if generator is None:
            raise ValueError("No generator connected to component")
        # Bus is always the second parameter in the tuple
        return RSCADIEEEG1.create(governor, self.base_frequency, generator)

    def create_rscad_pss(
        self, pss: PSS
    ) -> rscadPTIST1.rtdsPTIST1def | rscadPSS1A.rtdsPSS1Adef | None:
        """Check which RSCAD governor should be created"""
        if isinstance(pss, PTIST1):
            return self.create_rscad_ptist1(pss)
        if isinstance(pss, PSS1A):
            return self.create_rscad_pss1a(pss)
        return None

    def create_rscad_ptist1(self, pss: PTIST1) -> rscadPTIST1.rtdsPTIST1def:
        """Creates a RSCAD PTIST1 PSS from a datastructure PTIST1 PSS element and sets the available values"""
        generator = self.try_get_connected_generator(pss)
        if generator is None:
            raise ValueError("No generator connected to component")
        return RSCADPTIST1.create(pss, self.base_frequency, generator)

    def create_rscad_pss1a(self, pss: PSS1A) -> rscadPSS1A.rtdsPSS1Adef:
        """Creates a RSCAD PTIST1 PSS from a datastructure PTIST1 PSS element and sets the available values"""
        # Only Connection is the generator
        generator = self.try_get_connected_generator(pss)
        if generator is None:
            raise ValueError("No generator connected to component")
        return RSCADPSS1A.create(pss, self.base_frequency, generator)

    def try_get_connected_generator(self, component: Any) -> SynchronousMachine | None:
        """
        Tries to get the connected generator to a component.
        There should only be one generator connected to the component.
        """
        connected = list(self.graph.neighbors(component))
        if len(connected) == 0:
            return None
        connections = list(connected)
        for x in connected:
            connections = connections + list(self.graph.neighbors(x))
        generator = next((x for x in connections if isinstance(x, SynchronousMachine)), None)
        if generator is None:
            raise ValueError("No generator connected to component")
        return generator
