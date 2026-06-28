from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class OHLCV:
    timestamp_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float


def generate_synthetic_ohlcv(
    *,
    n: int = 300,
    seed: int = 42,
    start_ts_ms: int = 1_700_000_000_000,
    timeframe_ms: int = 60_000,
    start_price: float = 100.0,
) -> List[OHLCV]:
    """
    Single deterministic synthetic dataset generator (mock).

    Produces OHLCV bars that satisfy invariants:
    - timestamp_ms strictly increasing
    - high >= max(open, close)
    - low <= min(open, close)
    - open/close/low non-negative
    """
    assert n > 0, "n must be > 0"
    rng = random.Random(seed)

    price = float(start_price)
    out: List[OHLCV] = []

    for i in range(n):
        # random walk delta (small enough to keep numbers stable)
        delta = rng.uniform(-1.25, 1.25)
        o = price
        c = max(0.01, price + delta)

        # wick sizes
        wick_up = rng.uniform(0.0, 0.6)
        wick_down = rng.uniform(0.0, 0.6)

        h = max(o, c) + wick_up
        l = max(0.0, min(o, c) - wick_down)
        v = max(0.0, rng.uniform(100.0, 5000.0))

        out.append(
            OHLCV(
                timestamp_ms=start_ts_ms + i * timeframe_ms,
                open=o,
                high=h,
                low=l,
                close=c,
                volume=v,
            )
        )

        price = c

    return out
