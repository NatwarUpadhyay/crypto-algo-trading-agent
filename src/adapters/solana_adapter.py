from __future__ import annotations

import asyncio
from typing import Any, Mapping, Sequence

from src.adapters.base import (
    Balance,
    ExchangeAdapter,
    OHLCVBar,
    OrderResult,
    Position,
    Ticker,
    AdapterOrderError,
)


class SolanaDEXAdapter(ExchangeAdapter):
    """
    Solana DEX adapter (Jupiter/Raydium) - Phase 2 safe stub.

    - dry_run=True: returns deterministic placeholders.
    - dry_run=False: raises NotImplementedError (full integration comes later).
    """

    exchange_name = "solana"

    def __init__(
        self,
        *,
        dry_run: bool,
        solana_rpc_url: str = "",
        wallet_private_key: str = "",
        commitment: str = "confirmed",
        is_testnet: bool = True,
    ) -> None:
        super().__init__(dry_run=dry_run, is_testnet=is_testnet)
        self._solana_rpc_url = solana_rpc_url
        self._wallet_private_key = wallet_private_key
        self._commitment = commitment

    async def _dry_sleep(self) -> None:
        await asyncio.sleep(0)

    async def get_ticker(self, symbol: str) -> Ticker:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

        return Ticker(symbol=symbol, bid=1.0, ask=1.01, last=1.005, timestamp_ms=0)

    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> Sequence[OHLCVBar]:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

        n = max(0, min(limit, 5))
        bars: list[OHLCVBar] = []
        base_ts = 0
        for i in range(n):
            bars.append(
                OHLCVBar(
                    timestamp_ms=base_ts + i,
                    open=1.0 + i * 0.001,
                    high=1.01 + i * 0.001,
                    low=0.99 + i * 0.001,
                    close=1.005 + i * 0.001,
                    volume=1000.0,
                )
            )
        return bars

    async def get_balance(self) -> Sequence[Balance]:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

        return [
            Balance(asset="USDC", free=10000.0, total=10000.0),
            Balance(asset="SOL", free=2.0, total=2.0),
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
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

        if side not in {"buy", "sell"}:
            raise AdapterOrderError(f"Invalid side: {side}")
        if order_type not in {"market", "limit"}:
            raise AdapterOrderError(f"Invalid order_type: {order_type}")
        if amount <= 0:
            raise AdapterOrderError("amount must be > 0")

        return OrderResult(
            symbol=symbol,
            order_id="dry-run-swap-1",
            side=side,
            status="created",
            price=price,
            amount=amount,
            timestamp_ms=0,
        )

    async def cancel_order(self, symbol: str, order_id: str) -> OrderResult:
        await self._dry_sleep()
        if not self.dry_run:
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

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
            raise NotImplementedError("Solana live implementation is not included in Phase 2 scaffolding.")

        return [
            Position(
                symbol="SOL/USDC",
                side="long",
                quantity=0.5,
                entry_price=1.0,
                stop_loss_price=0.9,
                timestamp_ms=0,
            )
        ]
