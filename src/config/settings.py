"""
Configuration loader using pydantic-settings.

Reads from .env file and environment variables. All API keys and
sensitive data are stripped before any logging.
"""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    # ========================================================================
    # Trading Mode (Hard Limits)
    # ========================================================================
    dry_run: bool = Field(default=True, description="Enable dry-run mode (no live trades)")
    live_trading_confirmation: str = Field(
        default="",
        description="Required confirmation string to enable live trading (must match exact value in code)",
    )

    # ========================================================================
    # Exchange Configuration
    # ========================================================================
    # CCXT / Binance
    binance_api_key: SecretStr = Field(default=SecretStr(""), alias="BINANCE_API_KEY")
    binance_api_secret: SecretStr = Field(default=SecretStr(""), alias="BINANCE_API_SECRET")
    binance_testnet: bool = Field(default=True, description="Use Binance testnet")

    # Solana / Helius
    solana_rpc_url: str = Field(
        default="https://mainnet.helius-rpc.com/?api-key=YOUR_HELIUS_KEY",
        description="Solana RPC endpoint (Helius recommended)",
    )
    solana_wallet_private_key: SecretStr = Field(
        default=SecretStr(""), description="Solana wallet private key (base58)"
    )
    solana_commitment: str = Field(default="confirmed", description="Solana commitment level")

    # ========================================================================
    # Notifications
    # ========================================================================
    enable_telegram: bool = Field(default=False, description="Enable Telegram notifications")
    telegram_bot_token: SecretStr = Field(default=SecretStr(""), alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", description="Telegram chat ID for alerts")

    enable_webhook: bool = Field(default=False, description="Enable webhook notifications")
    webhook_url: str = Field(default="", description="Generic webhook URL for events")

    # ========================================================================
    # Database
    # ========================================================================
    database_url: str = Field(
        default="sqlite:///./crypto_trading.db", description="SQLAlchemy database URL"
    )

    # ========================================================================
    # Logging
    # ========================================================================
    log_level: str = Field(default="INFO", description="Root logger level")
    log_dir: Path = Field(default=Path("logs"), description="Log directory")
    log_file: str = Field(default="trading_agent.log", description="Log file name")

    # ========================================================================
    # Risk & Limits (Hard Limits — enforced in risk/ module)
    # ========================================================================
    max_notional_per_trade: float = Field(default=1000.0, description="Max notional per trade")
    max_daily_loss: float = Field(default=5000.0, description="Max daily loss (absolute USD)")
    max_daily_drawdown_percent: float = Field(
        default=10.0, description="Max daily drawdown (percent of equity)"
    )
    max_concurrent_positions: int = Field(default=5, description="Max concurrent open positions")
    order_cooldown_seconds: float = Field(default=5.0, description="Cooldown between orders")

    # ========================================================================
    # Backtest
    # ========================================================================
    backtest_data_dir: Path = Field(default=Path("data/cache"), description="Backtest cache dir")
    backtest_history_bars: int = Field(default=2000, description="Default history bars to fetch")
    backtest_timeframe: str = Field(default="1h", description="Default timeframe for backtest")

    # ========================================================================
    # MCP Server (Claude Integration)
    # ========================================================================
    mcp_server_host: str = Field(default="127.0.0.1", description="MCP server host")
    mcp_server_port: int = Field(default=8765, description="MCP server port")
    enable_mcp: bool = Field(default=False, description="Enable MCP server for Claude")

    # ========================================================================
    # Misc
    # ========================================================================
    debug: bool = Field(default=False, description="Enable debug logging")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_live_trading(self) -> bool:
        """
        Validate that live trading gates are satisfied.

        Returns True if live trading is allowed, False otherwise.
        Requires BOTH:
          1. dry_run == False
          2. live_trading_confirmation matches expected value
        """
        if self.dry_run:
            return False

        # This is intentionally vague; actual confirmation string is verified at startup
        expected_confirmation = "ENABLE_LIVE_TRADING_I_UNDERSTAND_THE_RISKS"
        return self.live_trading_confirmation == expected_confirmation
