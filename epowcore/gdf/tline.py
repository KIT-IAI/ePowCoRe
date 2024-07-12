from dataclasses import dataclass

from epowcore.generic.constants import Platform

from .component import Component


@dataclass(unsafe_hash=True, kw_only=True)
class TLine(Component):
    """This class represents a transmission line."""

    connector_names = ["A", "B"]

    length: float | None = None
    """Length of the line in km."""
    r1: float
    """Line resistance in Ohm per km. Absolute value if length is None."""
    x1: float
    """Line reactance in Ohm per km. Absolute value if length is None."""
    b1: float
    """Line susceptance in uS per km. Absolute value if length is None."""
    r0: float | None = None
    """Zero sequence resistance in Ohm per km. Absolute value if length is None."""
    x0: float | None = None
    """Zero sequence reactance in Ohm per km. Absolute value if length is None."""
    b0: float | None = None
    """Zero sequence susceptance in uS per km. Absolute value if length is None."""
    rating: float
    """Rating of the line in MVA."""
    rating_short_term: float | None = None
    """Rating of the line in MVA."""
    rating_emergency: float | None = None
    """Rating of the line in MVA."""
    parallel_lines: int = 1
    """Number of parallel lines."""
    angle_min: float | None = None
    """Minimum angle difference in degrees."""
    angle_max: float | None = None
    """Maximum angle differnce in degrees."""

    def r0_fb(self, platform: Platform | None = None, log: bool = True) -> float:
        """Fallback for r0 (zero sequence resistance) calculated with r1 and a configured factor.

        :param platform: The platform to get the configured factor for, defaults to None
        :type platform: Platform | None, optional
        :return: r0 if set, otherwise the calculated value
        :rtype: float
        """
        if self.r0 is not None:
            return self.r0
        factor = self.get_default("zero_sequence_factor", platform, log)
        if factor is None:
            raise ValueError("No default value found for `r0` calculation!")
        return self.r1 * factor

    def x0_fb(self, platform: Platform | None = None, log: bool = True) -> float:
        """Fallback for x0 (zero sequence reactance) calculated with x1 and a configured factor.

        :param platform: The platform to get the configured factor for, defaults to None
        :type platform: Platform | None, optional
        :return: x0 if set, otherwise the calculated value
        :rtype: float
        """
        if self.x0 is not None:
            return self.x0
        factor = self.get_default("zero_sequence_factor", platform, log)
        if factor is None:
            raise ValueError("No default value found for `x0` calculation!")
        return self.x1 * factor

    def b0_fb(self, platform: Platform | None = None, log: bool = True) -> float:
        """Fallback for b0 (zero sequence susceptance) calculated with b1 and a configured factor.

        :param platform: The platform to get the configured factor for, defaults to None
        :type platform: Platform | None, optional
        :return: b0 if set, otherwise the calculated value
        :rtype: float
        """
        if self.b0 is not None:
            return self.b0
        factor = self.get_default("zero_sequence_factor", platform, log)
        if factor is None:
            raise ValueError("No default value found for `b0` calculation!")
        return self.b1 * factor

    def rating_short_term_fb(self, platform: Platform | None = None, log: bool = True) -> float:
        """Fallback property for [rating_short_term]. Returns attribute if not None.
        Calculates the value with the [rating] and a given multiplicator.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        if self.rating_short_term is not None:
            return self.rating_short_term
        factor = self.get_default("rating_short_term_factor", platform, log)
        if factor is None:
            raise ValueError("No default value found for `rating_short_term` calculation!")
        return self.rating * factor

    def rating_emergency_fb(self, platform: Platform | None = None, log: bool = True) -> float:
        """Fallback property for [rating_emergency]. Returns attribute if not None.
        Calculates the value with the [rating] and a given multiplicator.

        :param platform: The platform to get the default value from, defaults to None
        :type platform: Platform | None, optional
        :return: The given or calculated value.
        :rtype: float
        """
        if self.rating_short_term is not None:
            return self.rating_short_term
        factor = self.get_default("rating_emergency_factor", platform, log)
        if factor is None:
            raise ValueError("No default value found for `rating_emergency` calculation!")
        return self.rating * factor
