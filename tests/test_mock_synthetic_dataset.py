from __future__ import annotations

from typing import Iterable

import pytest

from tests.mock_synthetic_dataset import generate_synthetic_ohlcv


def _assert_invariants(bars: Iterable) -> None:
    prev_ts = None
    for b in bars:
        ts = int(b.timestamp_ms)
        if prev_ts is not None:
            assert ts > prev_ts
        prev_ts = ts

        o = float(b.open)
        h = float(b.high)
        l = float(b.low)
        c = float(b.close)

        assert h >= max(o, c)
        assert l <= min(o, c)
        assert o >= 0.0
        assert c >= 0.0
        assert l >= 0.0


def test_mock_synthetic_dataset_is_deterministic() -> None:
    a = generate_synthetic_ohlcv(n=50, seed=123)
    b = generate_synthetic_ohlcv(n=50, seed=123)
    assert a == b


def test_mock_synthetic_dataset_invariants() -> None:
    bars = generate_synthetic_ohlcv(n=120, seed=42)
    assert len(bars) == 120
    _assert_invariants(bars)


def test_mock_synthetic_dataset_rejects_invalid_n() -> None:
    with pytest.raises(AssertionError):
        generate_synthetic_ohlcv(n=0)
