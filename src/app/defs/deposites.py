from dataclasses import dataclass

from .enums import SiteContent

@dataclass
class Restriction:
    min_efficiency: float
    max_efficiency: float
    max_reserve: float
    recovery_rate: float

BaseRestrictions: dict[SiteContent, Restriction] = {
    SiteContent.Fish: Restriction(
        min_efficiency=0.05,
        max_efficiency=0.5,
        max_reserve=10_000,
        recovery_rate=300
    ),
    SiteContent.Ferrite: Restriction(
        min_efficiency=0.08,
        max_efficiency=0.80,
        max_reserve=10_000,
        recovery_rate=200
    ),
    SiteContent.Pyrozine: Restriction(
        min_efficiency=0.1,
        max_efficiency=1.25,
        max_reserve=20_000,
        recovery_rate=100
    ),
}