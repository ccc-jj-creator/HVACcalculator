"""High level orchestration pipeline for the analyzer skeleton."""
from __future__ import annotations

import asyncio
from typing import Iterable

from .config import AnalyzerConfig
from .data.kalshi import KalshiClient
from .data.polymarket import PolymarketClient
from .data.news import NewsInterpreter, NewsStream, NewsEvent
from .models.belief_engine import BeliefEngine
from .opportunities import PositionSizing, detect_cross_venue_arbitrage, detect_mispricings
from .schemas import CanonicalEvent, Opportunity
from .execution.router import ExecutionRouter


class AnalyzerPipeline:
    """Coordinates the flow from data to execution."""

    def __init__(
        self,
        config: AnalyzerConfig,
        events: Iterable[CanonicalEvent],
        belief_engine: BeliefEngine,
        news_stream: NewsStream,
        news_interpreter: NewsInterpreter,
    ):
        self._config = config
        self._events = list(events)
        self._belief_engine = belief_engine
        self._news_stream = news_stream
        self._news_interpreter = news_interpreter
        self._router = ExecutionRouter()
        for event in self._events:
            self._belief_engine.initialize(event, base_probability=0.5)

    async def run_once(self) -> list[Opportunity]:
        polymarket = PolymarketClient()
        kalshi = KalshiClient()
        pm_quote = await anext(polymarket.stream_quotes())
        kalshi_quote = await anext(kalshi.stream_quotes())

        mapping = {event.event_id: event for event in self._events}
        news_events = [
            self._news_interpreter.to_signal(event, mapping)
            async for event in self._news_stream.stream()
        ]
        signals = [signal for signal in news_events if signal]
        forecast = self._belief_engine.update(self._events[0].event_id, signals)

        sizing = PositionSizing(bankroll=10_000, kelly_fraction=self._config.kelly_fraction)
        quotes = [pm_quote, kalshi_quote]
        mispricing = detect_mispricings(
            forecast,
            quotes,
            fee_key="taker",
            mispricing_threshold=self._config.mispricing_threshold,
            sizing=sizing,
        )
        cross = detect_cross_venue_arbitrage(
            pm_quote,
            kalshi_quote,
            fees=("trading", "maker"),
            threshold=self._config.mispricing_threshold,
        )
        tickets = self._router.route(mispricing + cross)
        return [
            Opportunity(
                event=mapping[ticket.event_id],
                venue=ticket.venue,
                side=ticket.side,
                price=ticket.price,
                expected_value=next(
                    (opp.expected_value for opp in mispricing + cross if opp.event.event_id == ticket.event_id and opp.side == ticket.side),
                    0.0,
                ),
                size=ticket.size,
                rationale=ticket.notes,
            )
            for ticket in tickets
        ]


async def anext(iterator):
    return await iterator.__anext__()


def demo_pipeline() -> list[Opportunity]:
    events = [
        CanonicalEvent(
            event_id="us_election_2028",
            description="Democrat wins 2028 US presidential election",
            resolution_date="2028-11-06",
            tags=("election", "us", "presidential"),
        )
    ]

    config = AnalyzerConfig(
        venues=[],
        news_sources=[],
        mispricing_threshold=0.02,
        kelly_fraction=0.25,
    )
    belief_engine = BeliefEngine(calibration_bias=0.01)
    news_stream = NewsStream(
        [
            NewsEvent(
                source="DowJones",
                topic="us_election_2028",
                body="New poll shows Democrat widening lead in key swing states.",
                bayes_factor=0.4,
            ),
            NewsEvent(
                source="NHC",
                topic="unrelated_event",
                body="Hurricane path update.",
                bayes_factor=0.1,
            ),
        ]
    )
    interpreter = NewsInterpreter(reliability=0.8)
    pipeline = AnalyzerPipeline(config, events, belief_engine, news_stream, interpreter)
    return asyncio.run(pipeline.run_once())
