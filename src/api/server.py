from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI

app = FastAPI(title="Crypto Algo Trading Agent API", version="0.1.0")


def _now_ms() -> int:
    return int(time.time() * 1000)


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "ts_ms": _now_ms()}


@app.get("/api/kpis")
async def kpis() -> dict[str, Any]:
    # Mock KPI response (until backtest/strategy/risk layers exist)
    return {
        "ts_ms": _now_ms(),
        "win_rate": 0.48,
        "max_drawdown": 0.12,
        "profit_factor": 1.35,
        "expectancy_r": 0.18,
        "signal_confidence": 0.62,
    }


@app.get("/api/market-structure")
async def market_structure() -> dict[str, Any]:
    # Mock upper-layer market structure signals
    return {
        "ts_ms": _now_ms(),
        "signals": {
            "fvg": {"strengths": [0.05, 0.12, 0.02, 0.18, 0.09]},
            "order_blocks": {
                "bullish": [{"zone": [100.0, 102.5], "strength": 0.31}],
                "bearish": [{"zone": [110.0, 112.0], "strength": 0.26}],
            },
            "liquidity_swaps": {
                "events": [{"type": "sweep_to_impulse", "dir": "up", "strength": 0.44}]
            },
        },
    }


@app.get("/api/positions")
async def positions() -> dict[str, Any]:
    # Mock positions
    return {
        "ts_ms": _now_ms(),
        "positions": [
            {"symbol": "BTC/USDT", "side": "long", "qty": 0.1, "entry": 100.0, "sl": 90.0},
            {"symbol": "SOL/USDC", "side": "long", "qty": 0.5, "entry": 1.0, "sl": 0.9},
        ],
    }
