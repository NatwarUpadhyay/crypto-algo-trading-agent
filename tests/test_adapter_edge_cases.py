from __future__ import annotations

import pytest

from src.adapters.ccxt_adapter import CCXTAdapter
from src.adapters.solana_adapter import SolanaDEXAdapter


@pytest.mark.asyncio
async def test_ccxt_dry_run_get_ohlcv_limit_bounds() -> None:
    adapter = CCXTAdapter(dry_run=True, exchange_id="binance")

    bars0 = await adapter.get_ohlcv("BTC/USDT", "1h", limit=0)
    assert len(bars0) == 0

    bars_neg = await adapter.get_ohlcv("BTC/USDT", "1h", limit=-10)
    assert len(bars_neg) == 0

    bars_10 = await adapter.get_ohlcv("BTC/USDT", "1h", limit=10)
    # stub caps to 5 bars for test speed
    assert len(bars_10) == 5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter_factory",
    [
        lambda: CCXTAdapter(dry_run=True, exchange_id="binance"),
        lambda: SolanaDEXAdapter(dry_run=True),
    ],
)
async def test_place_order_validations_side_and_amount(adapter_factory) -> None:
    adapter = adapter_factory()

    with pytest.raises(Exception):
        await adapter.place_order(
            "BTC/USDT",
            side="hold",  # invalid
            order_type="market",
            amount=1.0,
        )

    with pytest.raises(Exception):
        await adapter.place_order(
            "BTC/USDT",
            side="buy",
            order_type="market",
            amount=0,
        )

    with pytest.raises(Exception):
        await adapter.place_order(
            "BTC/USDT",
            side="buy",
            order_type="stop",  # invalid
            amount=1.0,
        )


@pytest.mark.asyncio
async def test_cancel_order_contract_returns_same_order_id() -> None:
    adapter = CCXTAdapter(dry_run=True, exchange_id="binance")

    order_id = "custom-order-x"
    canceled = await adapter.cancel_order("BTC/USDT", order_id)
    assert canceled.order_id == order_id


@pytest.mark.asyncio
async def test_open_positions_contains_stop_loss_in_stub() -> None:
    adapter = SolanaDEXAdapter(dry_run=True)
    positions = await adapter.get_open_positions()
    assert len(positions) > 0
    assert positions[0].stop_loss_price is not None

