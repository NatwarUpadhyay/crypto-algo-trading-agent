from __future__ import annotations

import pytest

try:
    import fastapi  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    pytest.skip("fastapi is not installed in this environment.", allow_module_level=True)

from fastapi.testclient import TestClient

from src.api.server import app


def test_health_endpoint() -> None:
    client = TestClient(app)  # type: ignore[operator]
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["ts_ms"], int)


def test_kpis_endpoint() -> None:
    client = TestClient(app)  # type: ignore[operator]
    resp = client.get("/api/kpis")
    assert resp.status_code == 200
    data = resp.json()

    required = ["win_rate", "max_drawdown", "profit_factor", "expectancy_r", "signal_confidence"]
    for k in required:
        assert k in data
    assert 0 <= data["win_rate"] <= 1
    assert data["profit_factor"] > 0
    assert 0 <= data["signal_confidence"] <= 1


def test_market_structure_endpoint() -> None:
    client = TestClient(app)  # type: ignore[operator]
    resp = client.get("/api/market-structure")
    assert resp.status_code == 200
    data = resp.json()
    assert "signals" in data

    signals = data["signals"]
    assert "fvg" in signals
    assert "order_blocks" in signals
    assert "liquidity_swaps" in signals


def test_positions_endpoint() -> None:
    client = TestClient(app)  # type: ignore[operator]
    resp = client.get("/api/positions")
    assert resp.status_code == 200
    data = resp.json()
    assert "positions" in data
    assert isinstance(data["positions"], list)
    assert all("symbol" in p and "side" in p for p in data["positions"])
