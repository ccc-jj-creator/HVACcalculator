"""Smart order routing skeleton."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..schemas import Opportunity, Venue


@dataclass
class OrderTicket:
    venue: Venue
    side: str
    size: float
    price: float
    event_id: str
    notes: str


class ExecutionRouter:
    """Dispatch opportunities to venue specific handlers."""

    def __init__(self):
        self._sent_orders: list[OrderTicket] = []

    def route(self, opportunities: Iterable[Opportunity]) -> list[OrderTicket]:
        tickets: list[OrderTicket] = []
        for opportunity in opportunities:
            if opportunity.size <= 0:
                continue
            ticket = OrderTicket(
                venue=opportunity.venue,
                side=opportunity.side,
                size=opportunity.size,
                price=opportunity.price,
                event_id=opportunity.event.event_id,
                notes=opportunity.rationale,
            )
            tickets.append(ticket)
        self._sent_orders.extend(tickets)
        return tickets

    @property
    def history(self) -> list[OrderTicket]:
        return list(self._sent_orders)
