"""Mispricing and arbitrage detection helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .schemas import Forecast, MarketQuote, Opportunity, Venue


@dataclass
class PositionSizing:
    bankroll: float
    kelly_fraction: float

    def size(self, probability: float, price: float) -> float:
        edge = probability - price
        if edge <= 0:
            return 0.0
        kelly = (probability - price) / (1 - price)
        kelly = max(min(kelly, 1.0), 0.0)
        return self.bankroll * self.kelly_fraction * kelly


def expected_value(probability: float, price: float, fee: float) -> float:
    return probability * (1 - fee) - price


def detect_mispricings(
    forecast: Forecast,
    quotes: Iterable[MarketQuote],
    fee_key: str,
    mispricing_threshold: float,
    sizing: PositionSizing,
) -> List[Opportunity]:
    opportunities: List[Opportunity] = []
    for quote in quotes:
        fee = quote.fees.get(fee_key, 0.0)
        ev = expected_value(forecast.probability, quote.yes_price, fee)
        if ev > mispricing_threshold:
            size = sizing.size(forecast.probability, quote.yes_price)
            opportunities.append(
                Opportunity(
                    event=forecast.event,
                    venue=quote.venue,
                    side="YES",
                    price=quote.yes_price,
                    expected_value=ev,
                    size=size,
                    rationale="Forecast probability exceeds tradeable price",
                )
            )
        short_ev = expected_value(1 - forecast.probability, 1 - quote.no_price, fee)
        if short_ev > mispricing_threshold:
            size = sizing.size(1 - forecast.probability, 1 - quote.no_price)
            opportunities.append(
                Opportunity(
                    event=forecast.event,
                    venue=quote.venue,
                    side="NO",
                    price=quote.no_price,
                    expected_value=short_ev,
                    size=size,
                    rationale="Forecast probability below market implied",
                )
            )
    return opportunities


def detect_cross_venue_arbitrage(
    pm_quote: MarketQuote,
    kalshi_quote: MarketQuote,
    fees: tuple[str, str],
    threshold: float,
) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    taker_fee, maker_fee = fees
    pm_cost = pm_quote.yes_price + pm_quote.fees.get(taker_fee, 0.0)
    kalshi_price = kalshi_quote.no_price - kalshi_quote.fees.get(maker_fee, 0.0)
    if pm_cost + kalshi_price < 1 - threshold:
        opportunities.append(
            Opportunity(
                event=pm_quote.event,
                venue=Venue.POLYMARKET,
                side="YES",
                price=pm_quote.yes_price,
                expected_value=1 - (pm_cost + kalshi_price),
                size=min(pm_quote.best_ask_size, kalshi_quote.best_bid_size),
                rationale="Cross-venue synthetic lock-in",
            )
        )
    return opportunities
