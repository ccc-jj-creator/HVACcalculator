"""Utilities for canonicalizing exchange specific markets."""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, Mapping

from .schemas import CanonicalEvent


@dataclass
class MarketMetadata:
    """Minimal metadata required to match exchange markets."""

    venue_event_id: str
    title: str
    resolution_date: str
    rules: str
    tags: tuple[str, ...]


class CanonicalizationService:
    """Maps venue specific markets to canonical event identifiers."""

    def __init__(self, canonical_events: Iterable[CanonicalEvent]):
        self._events = list(canonical_events)

    def best_match(self, metadata: MarketMetadata) -> CanonicalEvent | None:
        """Return the best canonical match above a similarity threshold."""

        scored: list[tuple[float, CanonicalEvent]] = []
        for event in self._events:
            similarity = self._score(metadata, event)
            if similarity > 0.6:  # heuristic threshold for skeleton usage
                scored.append((similarity, event))
        if not scored:
            return None
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def _score(self, metadata: MarketMetadata, event: CanonicalEvent) -> float:
        text = f"{metadata.title} {metadata.rules} {' '.join(metadata.tags)}"
        reference = f"{event.description} {' '.join(event.tags)}"
        return SequenceMatcher(None, text.lower(), reference.lower()).ratio()

    def add_event(self, event: CanonicalEvent) -> None:
        self._events.append(event)

    def snapshot(self) -> Mapping[str, CanonicalEvent]:
        return {event.event_id: event for event in self._events}
