from __future__ import annotations

import pytest

from src.config.settings import Settings


def test_settings_default_dry_run_true() -> None:
    s = Settings()
    assert s.dry_run is True
    assert s.validate_live_trading() is False


def test_settings_live_trading_gates_require_confirmation_exact_match() -> None:
    s = Settings(dry_run=False, live_trading_confirmation="")
    assert s.validate_live_trading() is False

    s_ok = Settings(
        dry_run=False, live_trading_confirmation="ENABLE_LIVE_TRADING_I_UNDERSTAND_THE_RISKS"
    )
    assert s_ok.validate_live_trading() is True


def test_settings_extra_fields_ignored() -> None:
    # pydantic Settings config has extra='ignore'
    s = Settings(dry_run=True, some_random_field="value")
    assert s.dry_run is True


def test_settings_can_override_log_dir(tmp_path) -> None:
    s = Settings(log_dir=tmp_path)
    assert s.log_dir == tmp_path


@pytest.mark.parametrize(
    "value",
    [
        "",
        "enable_live_trading_i_understand_the_risks",
        "ENABLE_LIVE_TRADING",
        "ENABLE_LIVE_TRADING_I_UNDERSTAND_THE_RISK",  # missing 'S'
    ],
)
def test_settings_live_trading_confirmation_must_match_exact(value: str) -> None:
    s = Settings(
        dry_run=False,
        live_trading_confirmation=value,
    )
    assert s.validate_live_trading() is False

