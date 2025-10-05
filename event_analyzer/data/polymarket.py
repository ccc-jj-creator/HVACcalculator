"""Polymarket market data client (skeleton)."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Callable, Iterable

from ..schemas import MarketQuote, Venue


@dataclass
class PolymarketConfig:
    market_channel: str = "wss://clob.polymarket.com/market"
    rest_base_url: str = "https://gamma-api.polymarket.com"


class PolymarketClient:
    """Async interface surface for the Polymarket CLOB websocket."""

    def __init__(self, config: PolymarketConfig | None = None):
        self._config = config or PolymarketConfig()

    async def connect(self) -> None:
        """Placeholder connect routine; replace with real websocket client."""

        await asyncio.sleep(0.01)

    async def stream_quotes(self) -> AsyncIterator[MarketQuote]:
        """Yield synthetic quotes to demonstrate the stream shape."""

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
            venue=Venue.POLYMARKET,
            yes_price=0.58,
            no_price=0.45,
            best_bid_size=1200,
            best_ask_size=950,
            fees={"trading": 0.0},
        )

    async def with_subscription(self, handler: Callable[[MarketQuote], None]) -> None:
        async for quote in self.stream_quotes():
            handler(quote)
