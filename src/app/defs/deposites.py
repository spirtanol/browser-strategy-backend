from dataclasses import dataclass

from .enums import SiteContent

@dataclass
class Restriction:
    min_efficiency: float
    max_efficiency: float
    max_reserve: float
    recovery_rate: float
    max_efficiency_threshold: float

BaseRestrictions: dict[SiteContent, Restriction] = {
    SiteContent.Fish: Restriction(
        min_efficiency=0.05,
        max_efficiency=0.5,
        max_reserve=10_000_000,
        recovery_rate=300_000,
        max_efficiency_threshold=0.8
    ),
    SiteContent.Ferrite: Restriction(
        min_efficiency=0.08,
        max_efficiency=0.80,
        max_reserve=10_000_000,
        recovery_rate=200_000,
        max_efficiency_threshold=0.8
    ),
    SiteContent.Pyrozine: Restriction(
        min_efficiency=0.1,
        max_efficiency=1.25,
        max_reserve=20_000_000,
        recovery_rate=100_000,
        max_efficiency_threshold=0.8
    ),
}