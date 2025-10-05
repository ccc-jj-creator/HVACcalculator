# Event Options Analyzer Skeleton

This repository provides a runnable skeleton for the real-time event options analyzer outlined in the product brief.  It focuses on three pillars:

1. **Belief formation** via Bayesian updating with lightweight calibration.
2. **Mispricing and arbitrage detection** for Polymarket and Kalshi style venues.
3. **Execution routing** that converts opportunities into venue-specific order tickets.

## Modules

- `event_analyzer/config.py` – typed configuration for venues, news sources, and risk knobs.
- `event_analyzer/canonicalization.py` – helper for mapping venue markets to canonical events.
- `event_analyzer/data/` – websocket client skeletons and a news interpreter that converts headlines into Bayesian signals.
- `event_analyzer/models/belief_engine.py` – Bayesian log-odds tracker with calibration bias and variance estimates.
- `event_analyzer/opportunities.py` – expected-value math, mispricing detection, and cross-venue arbitrage checks.
- `event_analyzer/execution/router.py` – converts opportunities into standardized order tickets.
- `event_analyzer/pipeline.py` – orchestrates a single run of the pipeline with synthetic data.

## Demo

Run the demo to see the pipeline assemble a forecast, evaluate synthetic quotes, and emit order tickets:

```bash
python - <<'PY'
from event_analyzer.pipeline import demo_pipeline

opportunities = demo_pipeline()
for opportunity in opportunities:
    print(opportunity)
PY
```

This prints the detected opportunities using the synthetic data sources included in the skeleton.  Replace the synthetic quote producers with authenticated websocket clients, wire in real news feeds, and plug the router into venue-specific order entry APIs to complete the system.
