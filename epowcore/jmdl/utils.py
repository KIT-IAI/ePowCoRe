from epowcore.jmdl.jmdl_model import Block


def clean(text: str) -> str:
    """Sanitizes a string to be used as a name in the easimov model.

    :param text: The string to be sanitized.
    :return: The sanitized string.
    """
    return (
        text.replace(" ", "")
        .replace("-", "_")
        .replace("(", "_")
        .replace(")", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace("#", "_")
    )


def get_coordinates(block: Block) -> tuple[float, float] | None:
    """Extracts the coordinates from the geoData of a block."""

    if not "geoData" in block.data.entries_dict:
        return None
    geo_data = block.data.entries_dict["geoData"].entries_dict
    if not "center" in geo_data:
        return None
    geo_data = geo_data["center"].value
    if len(geo_data.split(",")) not in (2, 3):
        return None
    c = geo_data.split(",")
    return (float(c[0]), float(c[1]))
