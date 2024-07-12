from dataclasses import dataclass, field
from math import ceil, sqrt

from epowcore.generic.constants import Platform
from epowcore.generic.logger import Logger

from .transformer import TapDetails, Transformer, WindingConfig, connections_for_phase_shift


# The attributes are never changed after being inserted into a structure requiring hashes
@dataclass(unsafe_hash=True, kw_only=True)
class TwoWindingTransformer(Transformer):
    """This class represents a transformer with two windings.

    p.u. values are based on the rating of the transformer.
    """

    connector_names = ["HV", "LV"]

    rating: float = field(default_factory=float)
    """Rating of the transformer in MVA."""
    rating_short_term: float | None = None
    """Rating of the transformer in MVA."""
    rating_emergency: float | None = None
    """Rating of the transformer in MVA."""
    voltage_hv: float
    """Voltage on the high voltage side in kV."""
    voltage_lv: float
    """Voltage on the low voltage side in kV."""
    r1pu: float
    """Short-circuit resistance (copper losses) in the transformer [p.u.]"""
    x1pu: float
    """Reactance of the positive sequequence impedance [p.u.]"""
    pfe_kw: float
    """No load losses (iron losses) of the transformer [kW]"""
    no_load_current: float
    """Magnetic no load current of the transformer [%]"""
    connection_type_hv: WindingConfig | None = None
    """The type of connection on the high voltage side."""
    connection_type_lv: WindingConfig | None = None
    """The type of connection on the low voltage side."""
    phase_shift_30: int
    """Phase shift from primary to secondary winding [30 deg]"""
    tap_changer_voltage: float | None = None
    """Voltage change per tap in p.u."""
    tap_min: int | None = None
    """Tap changer for negative direction in negative values"""
    tap_max: int | None = None
    """Tap changer for positive direction in positive values"""
    tap_neutral: int | None = None
    """Number where neutral position of the tap changer is at"""
    tap_initial: int | None = None
    """Number where initial position of the tap changer is at"""
    tap_ratio: float | None = None
    """Tap ratio"""
    angle_min: float | None = None
    """Minimum angle difference [deg]"""
    angle_max: float | None = None
    """Maximum angle differnce [deg]"""

    @property
    def connection_type_hv_fb(self) -> WindingConfig:
        """The type of connection on the high voltage side with fallback selection based on [phase_shift]."""
        if self.connection_type_hv is not None:
            return self.connection_type_hv
        Logger.log_to_selected(
            f"Using HV connection type based on phase shift for {self.name} ({self.phase_shift=})"
        )
        return connections_for_phase_shift(round(self.phase_shift))[0]

    @property
    def connection_type_lv_fb(self) -> WindingConfig:
        """The type of connection on the low voltage side with fallback selection based on [phase_shift]."""
        if self.connection_type_lv is not None:
            return self.connection_type_lv
        Logger.log_to_selected(
            f"Using LV connection type based on phase shift for {self.name} ({self.phase_shift=})"
        )
        return connections_for_phase_shift(round(self.phase_shift))[1]

    @property
    def phase_shift(self) -> float:
        """Phase shift from primary to secondary winding [deg]"""
        return self.phase_shift_30 * 30.0

    @property
    def pfe_pu(self) -> float:
        """No load losses (iron losses) of the transformer [p.u.]

        Same as gm_pu."""
        return self.gm_pu

    @property
    def ym_pu(self) -> float:
        """Magnetizing admittance [p.u.]

        ym = gm + j * bm
        """
        return self.no_load_current / 100

    @property
    def gm_pu(self) -> float:
        """Magnetizing conductance [p.u.]

        Same as pfe_pu."""
        return self.pfe_kw / (self.rating * 1000)

    @property
    def bm_pu(self) -> float:
        """Magnetizing susceptance [p.u.]"""
        return -1 * sqrt(self.ym_pu**2 - self.gm_pu**2)

    @property
    def zm_pu(self) -> float:
        """Magnetizing impedance [p.u.]"""
        return 1 / (self.no_load_current / 100)

    @property
    def rm_pu(self) -> float:
        """Magnetizing resistance (resistive iron losses) [p.u.]"""
        try:
            return self.rating / (self.pfe_kw / 1000)
        except ZeroDivisionError as exc:
            result = self.get_default("rm_pu")
            if result is None:
                raise ZeroDivisionError("No default value found for `rm_pu`!") from exc
            return result

    @property
    def xm_pu(self) -> float:
        """Magnetizing reactance [p.u.]"""
        try:
            return 1 / (sqrt(1 / self.zm_pu**2 - 1 / self.rm_pu**2))
        except ZeroDivisionError as exc:
            result = self.get_default("xm_pu")
            if result is None:
                raise ZeroDivisionError("No default value found for `xm_pu`!") from exc
            return result

    def rating_short_term_fb(self, platform: Platform | None = None) -> float:
        """Fallback property for [rating_short_term]. Returns attribute if not None.
        Calculates the value with the [rating] and a given multiplicator.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        if self.rating_short_term is not None:
            return self.rating_short_term
        factor = self.get_default("rating_short_term_factor", platform)
        if factor is None:
            raise ValueError("No default value found for `rating_short_term` calculation!")
        return self.rating * factor

    def rating_emergency_fb(self, platform: Platform | None = None) -> float:
        """Fallback property for [rating_emergency]. Returns attribute if not None.
        Calculates the value with the [rating] and a given multiplicator.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        if self.rating_short_term is not None:
            return self.rating_short_term
        factor = self.get_default("rating_emergency_factor", platform)
        if factor is None:
            raise ValueError("No default value found for `rating_emergency` calculation!")
        return self.rating * factor

    def tap_ratio_fb(self, platform: Platform | None = None) -> float:
        """Fallback property for [tap_ratio]. Returns attribute if not None.
        Calculates the ratio based on given tap information (voltage, initial and neutral position).
        Returns configured default value if no other information is present.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        if self.tap_ratio:
            return self.tap_ratio
        if (
            self.tap_changer_voltage is not None
            and self.tap_initial is not None
            and self.tap_neutral is not None
        ):
            return 1.0 + (self.tap_initial - self.tap_neutral) * self.tap_changer_voltage
        tap_ratio = self.get_default("tap_ratio", platform)
        if tap_ratio is None:
            raise ValueError("No default value found for `tap_ratio`!")
        return tap_ratio

    def get_tap_details_fb(self, platform: Platform | None = None) -> TapDetails:
        """Fallback property for all tap details except [tap_ratio]. Returns attributes if not None.
        Calculates the tap information based on the ratio and configured defaults.
        Returns configured default values if no other information is present.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        voltage = self.tap_changer_voltage
        tap_min = self.tap_min
        tap_max = self.tap_max
        tap_neutral = self.tap_neutral
        tap_initial = self.tap_initial
        if (
            voltage is None
            or tap_min is None
            or tap_max is None
            or tap_neutral is None
            or tap_initial is None
        ):
            # we assume that [tap_ratio] is the only information about the tap changer
            if self.tap_ratio is None:
                # even [tap_ratio] is not set -> return defaults
                Logger.log_to_selected(
                    f"No tap information for {type(self).__name__} '{self.name}'. Using configured default values."
                )

                voltage = self.get_default("tap_changer_voltage", platform)
                tap_min = self.get_default("tap_min", platform)
                tap_max = self.get_default("tap_max", platform)
                tap_neutral = self.get_default("tap_neutral", platform)
                tap_initial = self.get_default("tap_initial", platform)

                if (
                    voltage is None
                    or tap_min is None
                    or tap_max is None
                    or tap_neutral is None
                    or tap_initial is None
                ):
                    raise ValueError("Default value missing for tap details!")
                return TapDetails(voltage, tap_min, tap_max, tap_neutral, tap_initial)

            # calculate detailed tap information from given tap_ratio
            max_voltage = self.get_default("max_tap_voltage", platform)
            if max_voltage is None:
                raise ValueError("No default value found for `max_tap_voltage`!")
            num_steps: int = ceil(abs(self.tap_ratio - 1) / max_voltage)
            voltage = abs(self.tap_ratio - 1) / num_steps
            tap_min = -1 * num_steps
            tap_max = num_steps
            tap_neutral = 0
            tap_initial = num_steps if self.tap_ratio > 1 else -1 * num_steps
        return TapDetails(voltage, tap_min, tap_max, tap_neutral, tap_initial)
