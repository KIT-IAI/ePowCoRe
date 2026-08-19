from epowcore.power_factory.utils import get_coords


class FakePFObject:
    def __init__(
        self,
        class_name: str,
        gps_lat: float = 0.0,
        gps_lon: float = 0.0,
        parent=None,
    ) -> None:
        self._class_name = class_name
        self.GPSlat = gps_lat
        self.GPSlon = gps_lon
        self._parent = parent

    def GetClassName(self) -> str:
        return self._class_name

    def GetParent(self):
        return self._parent


def test_get_coords_keeps_component_coordinates() -> None:
    component = FakePFObject(
        class_name="ElmLod",
        gps_lat=49.01,
        gps_lon=8.41,
    )

    assert get_coords(component) == (49.01, 8.41)


def test_get_coords_inherits_coordinates_from_site() -> None:
    site = FakePFObject(
        class_name="ElmSite",
        gps_lat=49.02,
        gps_lon=8.42,
    )

    component = FakePFObject(
        class_name="ElmLod",
        parent=site,
    )

    assert get_coords(component) == (49.02, 8.42)


def test_get_coords_does_not_inherit_from_non_site_parent() -> None:
    parent = FakePFObject(
        class_name="ElmNet",
        gps_lat=49.03,
        gps_lon=8.43,
    )

    component = FakePFObject(
        class_name="ElmLod",
        parent=parent,
    )

    assert get_coords(component) is None


def test_get_coords_returns_none_if_site_has_default_coordinates() -> None:
    site = FakePFObject(
        class_name="ElmSite",
    )

    component = FakePFObject(
        class_name="ElmLod",
        parent=site,
    )

    assert get_coords(component) is None