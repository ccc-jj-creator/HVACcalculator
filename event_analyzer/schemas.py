"""Domain models shared across the analyzer modules."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping


class Venue(Enum):
    POLYMARKET = "polymarket"
    KALSHI = "kalshi"


@dataclass(frozen=True)
class CanonicalEvent:
    """Represents the canonical description of an event across venues."""

    event_id: str
    description: str
    resolution_date: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class MarketQuote:
    """Snapshot of a tradeable quote."""

    event: CanonicalEvent
    venue: Venue
    yes_price: float
    no_price: float
    best_bid_size: float
    best_ask_size: float
    fees: Mapping[str, float]

    @property
    def midpoint(self) -> float:
        return (self.yes_price + (1 - self.no_price)) / 2


@dataclass
class Signal:
    """A forecasting signal expressed as a Bayes factor in log-odds space."""

    name: str
    log_bayes_factor: float
    provenance: str
    weight: float = 1.0


@dataclass
class Forecast:
    """A calibrated probability estimate for an event."""

    event: CanonicalEvent
    probability: float
    variance: float
    contributing_signals: Iterable[Signal]


@dataclass
class Opportunity:
    """A potential trade with its expected value after fees."""

    event: CanonicalEvent
    venue: Venue
    side: str
    price: float
    expected_value: float
    size: float
    rationale: str
