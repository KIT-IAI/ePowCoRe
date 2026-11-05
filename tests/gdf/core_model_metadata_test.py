
from epowcore.gdf.core_model import CoreModel
import pandapower as pp
import pytest
from epowcore.pandapower.pandapower_converter import PandapowerConverter
from epowcore.pandapower.pandapower_model import PandapowerModel


def test_model_metadata_roundtrip():
    original = CoreModel(
        base_frequency=50.0,
        name="IEEE39",
        model_version="1.0",
    )

    data = original.export_dict()

    assert data["name"] == "IEEE39"
    assert data["model_version"] == "1.0"

    restored = CoreModel.import_dict(data)

    assert restored.name == "IEEE39"
    assert restored.model_version == "1.0"


def test_legacy_gdf_without_metadata():
    original = CoreModel(base_frequency=50.0)

    data = original.export_dict()
    data.pop("name")
    data.pop("model_version")

    restored = CoreModel.import_dict(data)

    assert restored.name == ""
    assert restored.model_version == ""

def test_pandapower_model_metadata_import():
    network = pp.create_empty_network(
        name="Test Grid",
        f_hz=50.0,
    )
    network["model_version"] = "1.2"

    converter = PandapowerConverter()
    core_model = converter.to_gdf(
        PandapowerModel(network=network)
    )

    assert core_model.name == "Test Grid"
    assert core_model.model_version == "1.2"



def test_pandapower_metadata_roundtrip():
    network = pp.create_empty_network(
        name="Test Grid",
        f_hz=50.0,
    )
    network["model_version"] = "1.2"

    converter = PandapowerConverter()

    gdf_model = converter.to_gdf(
        PandapowerModel(network=network)
    )

    reconstructed = converter.from_gdf(
        core_model=gdf_model,
        name="Test Grid",
    ).network

    assert reconstructed.name == "Test Grid"
    assert reconstructed["model_version"] == "1.2"


def test_pypsa_metadata_export():
    pytest.importorskip("pypsa")

    from epowcore.pypsa.pypsa_convert import PyPSAConverter

    model = CoreModel(
        base_frequency=50.0,
        name="Test Grid",
        model_version="1.2",
    )

    converter = PyPSAConverter()
    exported = converter.from_gdf(
        core_model=model,
        name="Fallback Name",
    )

    assert exported.name == "Test Grid"
    assert exported.meta["model_version"] == "1.2"


def test_jmdl_metadata_roundtrip():
    from epowcore.jmdl.jmdl_converter import JmdlConverter

    original = CoreModel(
        base_frequency=50.0,
        base_mva=100.0,
        name="Test Grid",
        model_version="1.2",
    )

    converter = JmdlConverter()

    # GDF -> JMDL
    jmdl_model = converter.from_gdf(
        core_model=original,
        name="Test Grid",
    )

    assert jmdl_model.data.entries_dict["modelName"].value == "Test Grid"
    assert jmdl_model.data.entries_dict["modelVersion"].value == "1.2"

    # JMDL -> GDF
    reconstructed = converter.to_gdf(jmdl_model)

    assert reconstructed.name == "Test Grid"
    assert reconstructed.model_version == "1.2"



def test_matpower_metadata_export():
    from epowcore.matpower.from_gdf.matpower_export import export_matpower

    original = CoreModel(
        base_frequency=50.0,
        base_mva=100.0,
        name="IEEE39",
        model_version="1.2",
    )

    exported = export_matpower(original)

    assert exported.name == "IEEE39"
    assert exported.model_version == "1.2"

    data = exported.as_dict()["mpc"]
    assert data["name"] == "IEEE39"
    assert data["model_version"] == "1.2"
    assert data["version"] == 2


def test_rscad_model_metadata_fields():
    pytest.importorskip("pyapi_rts")

    from epowcore.rscad.rscad_export import RscadModel

    model = RscadModel(
        draft=None,
        tli_files=[],
        name="Test Grid",
        model_version="1.2",
    )

    assert model.name == "Test Grid"
    assert model.model_version == "1.2"
