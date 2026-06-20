import inspect

import pytest

from src.adapters.base import Balance, ExchangeAdapter, OHLCVBar, OrderResult, Position, Ticker
from src.adapters.ccxt_adapter import CCXTAdapter
from src.adapters.solana_adapter import SolanaDEXAdapter


def _assert_is_async_callable(obj: object, name: str) -> None:
    assert hasattr(obj, name), f"Missing method: {name}"
    method = getattr(obj, name)
    assert callable(method), f"Method not callable: {name}"
    assert inspect.iscoroutinefunction(method), f"Method must be async: {name}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter",
    [
        CCXTAdapter(dry_run=True, exchange_id="binance"),
        SolanaDEXAdapter(dry_run=True),
    ],
)
async def test_adapter_contract_async_methods(adapter: ExchangeAdapter) -> None:
    _assert_is_async_callable(adapter, "get_ticker")
    _assert_is_async_callable(adapter, "get_ohlcv")
    _assert_is_async_callable(adapter, "get_balance")
    _assert_is_async_callable(adapter, "place_order")
    _assert_is_async_callable(adapter, "cancel_order")
    _assert_is_async_callable(adapter, "get_open_positions")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "adapter",
    [
        CCXTAdapter(dry_run=True, exchange_id="binance"),
        SolanaDEXAdapter(dry_run=True),
    ],
)
async def test_adapter_dry_run_return_shapes(adapter: ExchangeAdapter) -> None:
    ticker = await adapter.get_ticker("BTC/USDT")
    assert isinstance(ticker, Ticker)

    ohlcv = await adapter.get_ohlcv("BTC/USDT", "1h", limit=10)
    assert isinstance(ohlcv, (list, tuple))
    assert all(isinstance(b, OHLCVBar) for b in ohlcv)

    balances = await adapter.get_balance()
    assert isinstance(balances, (list, tuple))
    assert all(isinstance(b, Balance) for b in balances)

    positions = await adapter.get_open_positions()
    assert isinstance(positions, (list, tuple))
    assert all(isinstance(p, Position) for p in positions)

    order = await adapter.place_order(
        "BTC/USDT",
        side="buy",
        order_type="market",
        amount=1.0,
        price=None,
        stop_loss_price=0.9,
    )
    assert isinstance(order, OrderResult)
    assert order.order_id
    assert order.status

    canceled = await adapter.cancel_order("BTC/USDT", order.order_id)
    assert isinstance(canceled, OrderResult)
    assert canceled.order_id == order.order_id
