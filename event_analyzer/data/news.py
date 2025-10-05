"""Skeleton implementation for ingesting research and news feeds."""
from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from typing import AsyncIterator, Deque, Iterable

from ..schemas import CanonicalEvent, Signal


@dataclass
class NewsEvent:
    """Simplified representation of an incoming headline or filing."""

    source: str
    topic: str
    body: str
    bayes_factor: float


class NewsStream:
    """In-memory stream that mimics the interface of a real news feed."""

    def __init__(self, headlines: Iterable[NewsEvent]):
        self._queue: Deque[NewsEvent] = deque(headlines)

    async def stream(self) -> AsyncIterator[NewsEvent]:
        while self._queue:
            await asyncio.sleep(0.01)
            yield self._queue.popleft()


class NewsInterpreter:
    """Convert news events into Bayesian signals."""

    def __init__(self, reliability: float = 0.7):
        self._reliability = reliability

    def to_signal(self, event: NewsEvent, mapping: dict[str, CanonicalEvent]) -> Signal | None:
        canonical_event = mapping.get(event.topic)
        if not canonical_event:
            return None
        return Signal(
            name=f"news::{event.source}",
            log_bayes_factor=event.bayes_factor * self._reliability,
            provenance=event.body[:120],
            weight=self._reliability,
        )
