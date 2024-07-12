from dataclasses import field, dataclass
from enum import Enum
from .generator import Generator


class EPowGeneratorType(Enum):
    """Enum with possible JMDL generator types."""

    GAS = "Gas"
    WIND = "Wind"
    COAL = "Coal"
    PHOTOVOLTAIC = "Photovoltaic"
    HYDRO = "Hydro"
    SOLAR = "Solar"
    BATTERY = "Battery"
    BIOFUEL = "Biofuel"
    NUCLEAR = "Nuclear"
    TIDAL = "Tidal"
    OTHERS = "Others"


class EPowGeneratorCostModel(Enum):
    """Cost model for the generator."""

    NO_MODEL = "None"
    PIECEWISE_LINEAR = "Piecewise Linear"
    POLYNOMIAL = "Polynomial"


@dataclass(unsafe_hash=True)
class EPowGenerator(Generator):
    """Simple Generator imported from JMDL."""

    baseMVA: float = field(default_factory=float)
    """Base MVA of the generator"""
    voltageMagnitudeSetpoint: float = field(default_factory=float)
    """Voltage magnitude setpoint in p.u."""
    realPowerOutput: float = field(default_factory=float)
    """Real power output in MW."""
    reactivePowerOutput: float = field(default_factory=float)
    """Reactive power output in Mvar."""
    minimumRealPowerOutput: float = field(default_factory=float)
    """Minimum real power output in MW."""
    maximumRealPowerOutput: float = field(default_factory=float)
    """Maximum real power output in MW."""
    minimumReactivePowerOutput: float = field(default_factory=float)
    """Minimum reactive power output in Mvar."""
    maximumReactivePowerOutput: float = field(default_factory=float)
    """Maximum reactive power output in Mvar."""
    lowerPqCapabilityLimit: float = field(default_factory=float)
    """Lower PQ capability limit in p.u."""
    upperPqCapabilityLimit: float = field(default_factory=float)
    """Upper PQ capability limit in p.u."""
    pc1MinimumReactivePowerOutput: float = field(default_factory=float)
    """PC1 minimum reactive power output in Mvar."""
    pc1MaximumReactivePowerOutput: float = field(default_factory=float)
    """PC1 maximum reactive power output in Mvar."""
    pc2MinimumReactivePowerOutput: float = field(default_factory=float)
    """PC2 minimum reactive power output in Mvar."""
    pc2MaximumReactivePowerOutput: float = field(default_factory=float)
    """PC2 maximum reactive power output in Mvar."""
    areaParticipationFactor: float = field(default_factory=float)
    """Area participation factor"""
    ePowGeneratorType: EPowGeneratorType = field(default=EPowGeneratorType.OTHERS)
    """Type of the generator"""
