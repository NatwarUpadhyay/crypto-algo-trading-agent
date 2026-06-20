from __future__ import annotations

import asyncio
from typing import Any, Mapping, Sequence

from src.adapters.base import (
    AdapterConnectionError,
    AdapterDataError,
    AdapterError,
    AdapterOrderError,
    Balance,
    ExchangeAdapter,
    OHLCVBar,
    OrderResult,
    Position,
    Ticker,
)


class CCXTAdapter(ExchangeAdapter):
    """
    CCXT adapter.

    Phase 2 scaffolding approach:
    - dry_run=True: no network calls; returns deterministic placeholders that satisfy contract tests.
    - dry_run=False: NotImplementedError (full CCXT integration comes in later iteration).
    """

    exchange_name = "ccxt"

    def __init__(
        self,
        *,
        dry_run: bool,
        exchange_id: str = "binance",
        api_key: str = "",
        api_secret: str = "",
        is_testnet: bool = True,
    ) -> None:
        super().__init__(dry_run=dry_run, is_testnet=is_testnet)
        self._exchange_id = exchange_id
        self._api_key = api_key
        self._api_secret = api_secret

    async def _dry_sleep(self) -> None:
        # keep interface async-friendly without doing real I/O
        await asyncio.sleep(0)

    async def get_ticker(self, symbol: str) -> Ticker:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        return Ticker(
            symbol=symbol,
            bid=100.0,
            ask=101.0,
            last=100.5,
            timestamp_ms=0,
        )

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> Sequence[OHLCVBar]:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        # Return a minimal sequence that respects `limit` (bounded for test speed)
        n = max(0, min(limit, 5))
        bars: list[OHLCVBar] = []
        base_ts = 0
        for i in range(n):
            bars.append(
                OHLCVBar(
                    timestamp_ms=base_ts + i,
                    open=100.0 + i,
                    high=101.0 + i,
                    low=99.0 + i,
                    close=100.5 + i,
                    volume=10.0,
                )
            )
        return bars

    async def get_balance(self) -> Sequence[Balance]:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        return [
            Balance(asset="USDT", free=10000.0, total=10000.0),
            Balance(asset="BTC", free=1.0, total=1.0),
        ]

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: float | None = None,
        *,
        stop_loss_price: float | None = None,
        extra: Mapping[str, Any] | None = None,
    ) -> OrderResult:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        # Minimal validation for contract sanity
        if side not in {"buy", "sell"}:
            raise AdapterOrderError(f"Invalid side: {side}")
        if order_type not in {"market", "limit"}:
            raise AdapterOrderError(f"Invalid order_type: {order_type}")
        if amount <= 0:
            raise AdapterOrderError("amount must be > 0")

        return OrderResult(
            symbol=symbol,
            order_id="dry-run-order-1",
            side=side,
            status="created",
            price=price,
            amount=amount,
            timestamp_ms=0,
        )

    async def cancel_order(self, symbol: str, order_id: str) -> OrderResult:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        return OrderResult(
            symbol=symbol,
            order_id=order_id,
            side="buy",
            status="canceled",
            price=None,
            amount=None,
            timestamp_ms=0,
        )

    async def get_open_positions(self) -> Sequence[Position]:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("CCXT live implementation is not included in Phase 2 scaffolding.")

        return [
            Position(
                symbol="BTC/USDT",
                side="long",
                quantity=0.1,
                entry_price=100.0,
                stop_loss_price=90.0,
                timestamp_ms=0,
            )
        ]
