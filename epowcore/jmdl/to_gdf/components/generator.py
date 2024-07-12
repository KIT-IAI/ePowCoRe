from epowcore.gdf.generators.epow_generator import EPowGenerator, EPowGeneratorType
from epowcore.jmdl.jmdl_model import Block
from epowcore.jmdl.utils import get_coordinates


def create_generator(block: Block, uid: int) -> EPowGenerator:
    gen_data = block.data.entries_dict["EPowGenerator"]

    return EPowGenerator(
        uid,
        block.name,
        get_coordinates(block),
        gen_data.entries_dict["baseMVA"].value,  # Base MVA
        gen_data.entries_dict["V"].value,  # voltage magnitude
        gen_data.entries_dict["P"].value,  # active power
        gen_data.entries_dict["Q"].value,  # reactive power
        gen_data.entries_dict["Pmin"].value,  # Minimum active power
        gen_data.entries_dict["Pmax"].value,  # Maximum active power
        gen_data.entries_dict["Qmin"].value,  # Minimum reactive power
        gen_data.entries_dict["Qmax"].value,  # Maximum reactive power
        gen_data.entries_dict["PC1"].value,  # Lower active power of PQ curve
        gen_data.entries_dict["PC2"].value,  # Upper active power of PQ curve
        gen_data.entries_dict["QC1Min"].value,  # Minimum reactive power of PQ curve
        gen_data.entries_dict["QC1Max"].value,  # Maximum reactive power of PQ curve
        gen_data.entries_dict["QC2Min"].value,  # Minimum reactive power of PQ curve
        gen_data.entries_dict["QC2Max"].value,  # Maximum reactive power of PQ curve
        gen_data.entries_dict["APF"].value,  # Area participation factor
        EPowGeneratorType(gen_data.entries_dict["type"].value),  # Generator type
    )
