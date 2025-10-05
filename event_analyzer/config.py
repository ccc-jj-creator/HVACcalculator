"""Configuration objects for the event options analyzer skeleton."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class VenueConfig:
    """Connection configuration for a single trading venue."""

    name: str
    websocket_url: str
    rest_url: str
    api_key: str | None = None
    secret: str | None = None
    fee_schedule: Mapping[str, float] | None = None


@dataclass(frozen=True)
class NewsSourceConfig:
    """Configuration for a machine readable news feed or primary source."""

    name: str
    transport: str
    endpoint: str
    topics: Sequence[str]


@dataclass(frozen=True)
class AnalyzerConfig:
    """Top level configuration grouping all runtime concerns."""

    venues: Sequence[VenueConfig]
    news_sources: Sequence[NewsSourceConfig]
    mispricing_threshold: float
    kelly_fraction: float
