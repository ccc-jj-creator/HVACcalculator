"""Kalshi market data client (skeleton)."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Callable, Iterable

from ..schemas import MarketQuote, Venue


@dataclass
class KalshiConfig:
    websocket_url: str = "wss://api.kalshi.com/trade-api/ws"
    rest_base_url: str = "https://api.kalshi.com/trade-api/v2"


class KalshiClient:
    """Async interface surface for the Kalshi websocket."""

    def __init__(self, config: KalshiConfig | None = None):
        self._config = config or KalshiConfig()

    async def connect(self) -> None:
        await asyncio.sleep(0.01)

    async def stream_quotes(self) -> AsyncIterator[MarketQuote]:
        await self.connect()
        for quote in self._synthetic_quotes():
            await asyncio.sleep(0.01)
            yield quote

    def _synthetic_quotes(self) -> Iterable[MarketQuote]:
        from ..schemas import CanonicalEvent

        event = CanonicalEvent(
            event_id="us_election_2028",
            description="Democrat wins 2028 US presidential election",
            resolution_date="2028-11-06",
            tags=("election", "us", "presidential"),
        )
        yield MarketQuote(
            event=event,
            venue=Venue.KALSHI,
            yes_price=0.52,
            no_price=0.5,
            best_bid_size=800,
            best_ask_size=1030,
            fees={"taker": 0.07, "maker": 0.02},
        )

    async def with_subscription(self, handler: Callable[[MarketQuote], None]) -> None:
        async for quote in self.stream_quotes():
            handler(quote)
