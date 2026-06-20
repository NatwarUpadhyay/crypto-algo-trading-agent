from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping, Sequence, Final


class AdapterError(Exception):
    """Base error for exchange adapter failures."""


class AdapterConnectionError(AdapterError):
    """Raised when the adapter cannot reach the upstream venue."""


class AdapterDataError(AdapterError):
    """Raised when adapter receives malformed or missing data."""


class AdapterOrderError(AdapterError):
    """Raised when order placement/cancellation fails."""


@dataclass(frozen=True)
class Ticker:
    symbol: str
    bid: float | None
    ask: float | None
    last: float | None
    timestamp_ms: int | None = None


@dataclass(frozen=True)
class OHLCVBar:
    timestamp_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Balance:
    # asset -> free amount (or available) and total (if known)
    asset: str
    free: float
    total: float | None = None


@dataclass(frozen=True)
class OrderResult:
    symbol: str
    order_id: str
    side: str  # "buy" | "sell"
    status: str  # "created" | "filled" | "canceled" etc.
    price: float | None = None
    amount: float | None = None
    timestamp_ms: int | None = None


@dataclass(frozen=True)
class Position:
    symbol: str
    side: str  # "long" | "short"
    quantity: float
    entry_price: float
    stop_loss_price: float | None = None
    timestamp_ms: int | None = None


class ExchangeAdapter(ABC):
    """
    Venue-agnostic async adapter interface.

    Contract:
    - All public methods are async.
    - Return dataclasses defined in this module.
    - Implementations must honor dry_run in a safe manner (no network calls if possible).
    """

    exchange_name: Final[str]
    is_testnet: Final[bool]

    def __init__(self, *, dry_run: bool, is_testnet: bool = True) -> None:
        self._dry_run = dry_run
        self.is_testnet = is_testnet

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        raise NotImplementedError

    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int) -> Sequence[OHLCVBar]:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(self) -> Sequence[Balance]:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(self, symbol: str, order_id: str) -> OrderResult:
        raise NotImplementedError

    @abstractmethod
    async def get_open_positions(self) -> Sequence[Position]:
        raise NotImplementedError
