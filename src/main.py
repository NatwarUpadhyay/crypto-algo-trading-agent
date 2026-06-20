"""
Main entry point for the crypto algo trading agent.

Usage:
    python -m src.main

The agent will:
  1. Load configuration from .env
  2. Initialize logging (JSON file + console)
  3. Validate hard limits (DRY_RUN, live trading gates)
  4. (Phase 2+) Initialize exchange adapters
  5. (Phase 3+) Load strategies and backtest engine
  6. (Phase 4+) Start execution loop with risk layer
  7. (Phase 5+) Start MCP server for Claude advisory
"""

import asyncio
import logging
import sys
from pathlib import Path

from src.config.settings import Settings
from src.logging_setup import setup_logging


async def main() -> int:
    """
    Main async entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Load configuration
    try:
        settings = Settings()
    except Exception as e:
        print(f"Failed to load settings: {e}", file=sys.stderr)
        return 1

    # Initialize logging
    root_logger = setup_logging(
        log_dir=settings.log_dir,
        log_file=settings.log_file,
        log_level=settings.log_level,
    )
    logger = logging.getLogger(__name__)

    logger.info("=" * 80)
    logger.info("Crypto Algo Trading Agent Starting")
    logger.info("=" * 80)

    # ========================================================================
    # Validate hard limits and gates
    # ========================================================================
    if settings.dry_run:
        logger.info("DRY_RUN=true — no live trades will be executed")
    else:
        logger.warning("DRY_RUN=false — LIVE TRADING ENABLED")

        # Validate live trading confirmation
        if not settings.validate_live_trading():
            logger.error(
                "Live trading confirmation not satisfied. "
                "Set both DRY_RUN=false and provide live_trading_confirmation string."
            )
            return 1

        logger.warning("Live trading gates satisfied — execution enabled")

    # Log key configuration (no secrets)
    logger.info(
        f"Max notional per trade: ${settings.max_notional_per_trade}",
        extra={"exchange": "CCXT/Solana"},
    )
    logger.info(
        f"Max daily loss: ${settings.max_daily_loss} "
        f"({settings.max_daily_drawdown_percent}% of equity)"
    )
    logger.info(f"Max concurrent positions: {settings.max_concurrent_positions}")
    logger.info(f"Order cooldown: {settings.order_cooldown_seconds}s")

    # ========================================================================
    # Phase 1 Complete: Configuration & Logging Active
    # ========================================================================
    logger.info("Configuration loaded, logging initialized")
    logger.info("Ready for Phase 2: Exchange Adapters")

    # Placeholder for subsequent phases
    logger.info("Waiting for Phase 2+ implementation...")

    return 0


def entry_point() -> None:
    """CLI entry point (from pyproject.toml scripts)."""
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
