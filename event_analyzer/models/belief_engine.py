"""Belief engine implementing Bayesian log-odds updating with calibration."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, List

from ..schemas import CanonicalEvent, Forecast, Signal


@dataclass
class BeliefState:
    event: CanonicalEvent
    logit_probability: float
    history: List[Signal] = field(default_factory=list)

    @property
    def probability(self) -> float:
        odds = math.exp(self.logit_probability)
        return odds / (1 + odds)


class BeliefEngine:
    """Maintains calibrated beliefs for each canonical event."""

    def __init__(self, calibration_bias: float = 0.0):
        self._states: dict[str, BeliefState] = {}
        self._calibration_bias = calibration_bias

    def initialize(self, event: CanonicalEvent, base_probability: float) -> None:
        logit = self._to_logit(self._clamp(base_probability))
        self._states[event.event_id] = BeliefState(event=event, logit_probability=logit)

    def update(self, event_id: str, signals: Iterable[Signal]) -> Forecast:
        state = self._states[event_id]
        total_bayes = sum(signal.log_bayes_factor for signal in signals)
        state.logit_probability += total_bayes
        state.history.extend(signals)
        calibrated_probability = self._calibrate(state.probability)
        return Forecast(
            event=state.event,
            probability=calibrated_probability,
            variance=self._estimate_variance(state.history),
            contributing_signals=list(state.history),
        )

    def _calibrate(self, probability: float) -> float:
        return self._clamp(probability + self._calibration_bias)

    def _estimate_variance(self, signals: Iterable[Signal]) -> float:
        weight_sum = sum(signal.weight for signal in signals)
        if weight_sum == 0:
            return 0.25
        return 1 / (1 + weight_sum)

    @staticmethod
    def _to_logit(probability: float) -> float:
        return math.log(probability / (1 - probability))

    @staticmethod
    def _clamp(probability: float) -> float:
        return min(max(probability, 1e-6), 1 - 1e-6)
