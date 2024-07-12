import powerfactory as pf

from epowcore.gdf.external_grid import ExternalGrid, ExternalGridType
from epowcore.power_factory.utils import get_coords


def create_external_grid(pf_extgrid: pf.DataObject, uid: int) -> ExternalGrid:
    """Create an external grid component from a PowerFactory DataObject."""

    return ExternalGrid(
        uid,
        pf_extgrid.loc_name,
        get_coords(pf_extgrid),
        u_setp=pf_extgrid.usetp,
        p=pf_extgrid.pgini,
        q=pf_extgrid.qgini,
        q_min=pf_extgrid.cQ_min,
        q_max=pf_extgrid.cQ_max,
        bus_type=_EXTERNAL_GRID_TYPE[pf_extgrid.bustp],
    )


_EXTERNAL_GRID_TYPE = {
    "PQ": ExternalGridType.PQ,
    "PV": ExternalGridType.PV,
    "SL": ExternalGridType.SL,
}
