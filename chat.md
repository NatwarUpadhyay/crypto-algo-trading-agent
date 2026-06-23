# Crypto Algo Trading Agent — Session Chat History

**Date**: 2026-06-20  
**Status**: Phase 1 complete, Phase 2 ready to start

---

## Phase 0 — Architecture Confirmation & Decisions

### Initial Setup
User provided seed prompt (CLAUDE.md) with:
- **Architecture**: Python 3.11+, async (asyncio), two exchange adapters (CCXT + Solana DEX)
- **Strategy layer**: Pluggable base class, two reference strategies (MA crossover, RSI mean-reversion)
- **Risk & execution**: Deterministic, rule-based, no LLM in hot path
- **Claude advisory**: Separate async module, reviews backtests, proposes params, writes to review queue
- **Persistence**: SQLite (upgradeable to Postgres), pydantic-settings config
- **Hard limits**: DRY_RUN gates, max notional, max daily loss, kill switch, concurrent position cap, stop-loss requirement, order cooldown, kill switch test

### Phase 0 Clarifying Questions & Answers

**Q1: Testing & Code Quality**
- Framework: pytest + pytest-asyncio
- Typing: **mypy strict only on `risk/`, `execution/`, `adapters/`** (safety-critical path); relax elsewhere for iteration speed
- Pydantic v2 (implied by pydantic-settings)

**Q2: Database Layer**
- SQLAlchemy ORM (not raw SQL, schema integrity required)
- Skip Alembic until post-MVP, schema stabilizes first
- Trade ledger: **read-only** to advisory module (analysis only)
- Review queue: advisory module writes here, not to live config

**Q3: Notifications**
- Common `Notifier` interface, both independently toggleable
- **Telegram**: urgent alerts (kill-switch, errors) — phone-reachable
- **Webhook**: generic fallback/integration point

**Q4: MCP Server**
- **Separate async process**, isolated from live execution loop
- Exposed tools (read-only or write to review queue only):
  - `query_backtest`
  - `get_live_positions` (read-only)
  - `fetch_ohlcv`
  - `get_trade_ledger` (read-only)
  - `get_kill_switch_status` (read-only)
  - `propose_strategy_param_change` (writes to review queue)
- **DO NOT expose**: `place_order`, `cancel_order` (Claude stays out of hot path)

**Q5: Exchange Defaults**
- CCXT: **Binance** (testnet available, docs, prior art)
- Solana RPC: **Helius** (purpose-built for trading bots, free tier, webhooks; not Magic Eden which is NFT-pass marketplace)

**Q6: Backtest Data**
- Source: CCXT `fetch_ohlcv` → Parquet cache (not CSV)
- Default history: ~2 years or 1500–2000 bars (whichever is less), configurable per timeframe
- Sufficient for multiple market cycles + real drawdown analysis

**Q7: Logging**
- Dual handlers: JSON to file (advisory/dashboard parsing), human-readable to console (dev)
- Structured logging for kill-switch, trade fills, etc.

**Folder Structure**: Keep `src/` layout for cleaner packaging later

---

## Phase 1 — Scaffolding & Configuration (COMPLETE)

### Files Created

#### Core Configuration & Logging
- **`pyproject.toml`**: 
  - Dependencies: ccxt, solana-py, httpx, pydantic, pydantic-settings, sqlalchemy, pandas, pyarrow, structlog, python-json-logger, python-telegram-bot, mcp
  - Optional groups: `[dev]` (mypy, black, isort, ruff), `[test]` (pytest, pytest-asyncio, pytest-cov), `[mcp]`
  - Tool config: mypy (strict on safety-critical), pytest, black, isort, ruff
  - Scripts: `crypto-trading-agent` entry point

- **`src/config/settings.py`**:
  - 40+ config fields via pydantic-settings, reading from `.env`
  - Fields grouped: trading mode, CCXT/Binance, Solana/Helius, notifications, database, logging, risk limits, backtest data, MCP server, misc
  - SecretStr for API keys (never logged)
  - `validate_live_trading()` method enforces both gates
  - Defaults: DRY_RUN=true, Binance testnet, SQLite, all keys empty

- **`src/config/__init__.py`**: Exports Settings class

- **`src/logging_setup.py`**:
  - `setup_logging()` function creates dual handlers
  - Handler 1: JSON to file (`logs/trading_agent.log`) with jsonlogger
  - Handler 2: Console (human-readable) with formatted timestamps
  - structlog configured for event logging (JSON renderers, timestamp, stack info)

#### Entry Point
- **`src/main.py`**:
  - Async entry point with `main()` and `entry_point()` functions
  - Loads config → initializes logging → validates hard limits
  - Logs trading mode (DRY_RUN) and validates live trading gates
  - Logs key config (no secrets) — max notional, max daily loss, max positions, order cooldown
  - Placeholder for Phase 2+ implementation
  - Exits cleanly with proper async/sync handling

#### Module Initialization
- **`src/__init__.py`**: Version and package info
- **`src/adapters/__init__.py`**: (empty, ready for Phase 2)
- **`src/strategies/__init__.py`**: (empty, ready for Phase 3)
- **`src/risk/__init__.py`**: (empty, ready for Phase 4)
- **`src/execution/__init__.py`**: (empty, ready for Phase 4)
- **`src/backtest/__init__.py`**: (empty, ready for Phase 3)
- **`src/advisory/__init__.py`**: (empty, ready for Phase 5)
- **`src/data/__init__.py`**: (empty, ready for Phase 2+)
- **`src/notifications/__init__.py`**: (empty, ready for Phase 6)
- **`tests/__init__.py`**: (empty, pytest discovery)

#### Environment & Git
- **`.env.example`**:
  - All 40+ config keys present with empty/example values (safe to commit)
  - Organized sections: TRADING MODE, EXCHANGE CONFIGURATION, NOTIFICATIONS, DATABASE, LOGGING, RISK & LIMITS, BACKTEST, MCP SERVER, MISC
  - Includes comments for each key

- **`.gitignore`**:
  - Python: `__pycache__/`, `*.pyc`, `*.egg-info/`, `env/`, `venv/`, etc.
  - Testing: `.pytest_cache/`, `.coverage`, `htmlcov/`
  - IDE: `.vscode/`, `.idea/`, `*.swp`, `.DS_Store`
  - Project: `logs/`, `*.db`, `.cache/`, `.mcp/`, `mcp_logs/`
  - **Most importantly**: `.env` (never commit real keys)

#### Documentation
- **`CLAUDE.md`**: Seed prompt (Section A for Claude Code, Section B notes for user)

- **`README.md`** (350+ lines):
  - **Quick Start**: Prerequisites, clone & setup, configure .env, run Phase 1
  - **Architecture Diagram**: Mermaid graph showing all layers (Client, Backtest, Strategy, Claude Advisory, MCP Server, Execution Loop, Venues, Storage, Notifications)
  - **Project Structure**: Full folder tree
  - **Dependency Highlights**: Table of key packages with purposes
  - **Hard Limits Table**: DRY_RUN gate, max notional, max daily loss, max drawdown, max positions, stop-loss requirement, order cooldown, kill switch test
  - **Going Live Checklist**: 20+ items organized by category (Configuration, Risk Layer, Notifications, Backtest, Execution, Advisor Integration, Final Checks)
  - **Phase Roadmap**: Status table for all 8 phases
  - **Testing**: Command examples (pytest, coverage, async, watch)
  - **Type Checking**: mypy strict on critical path
  - **Code Quality**: black, isort, ruff commands
  - **Logging**: Explanation of dual handlers with JSON example
  - **FAQ**: 4 questions (Why CCXT + Solana?, Why no Claude in execution loop?, Going live with real capital?, New exchange?)
  - **References**: Links to CCXT, Solana-py, Pydantic, SQLAlchemy, Helius, Jupiter, Freqtrade, MCP
  - **Next Steps**: Copy .env.example, run Phase 1, continue to Phase 2

### Folder Structure Created
```
crypto_algo_trading_agent/
├── src/
│   ├── adapters/              (ready for Phase 2)
│   ├── strategies/            (ready for Phase 3)
│   ├── risk/                  (ready for Phase 4)
│   ├── execution/             (ready for Phase 4)
│   ├── backtest/              (ready for Phase 3)
│   ├── advisory/              (ready for Phase 5)
│   ├── data/                  (ready for Phase 2+)
│   ├── notifications/         (ready for Phase 6)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── main.py
│   ├── logging_setup.py
│   └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── .env.example
├── .gitignore
├── CLAUDE.md
└── README.md
```

### Key Features Implemented

#### Configuration System (pydantic-settings)
- **40+ fields** with secure defaults
- **Environment reading**: .env file + environment variables
- **Type safety**: pydantic v2 validation
- **Secrets handling**: SecretStr for API keys
- **Validation**: `validate_live_trading()` method checks both gates

#### Logging System (Dual-Handler)
- **File handler**: JSON output to `logs/trading_agent.log` (structured, parseable)
  - Format: timestamp, level, logger name, message
  - Supports custom fields for events (e.g., event_type="trade_fill")
  
- **Console handler**: Human-readable to stdout
  - Format: `[YYYY-MM-DD HH:MM:SS] LEVEL module: message`
  - For development, easy debugging

- **structlog integration**:
  - Processors for stack info, exception rendering, JSON output
  - Context-aware logging for multi-threaded/async scenarios

#### Testing Setup (pytest + asyncio)
- **pytest** configured with:
  - `asyncio_mode = "auto"` for pytest-asyncio
  - Markers: `unit`, `integration`, `asyncio`
  - testpaths: `tests/`
  
- **Coverage target**: 80%+ on `src/risk/` and `src/execution/`
- **Type checking**: mypy strict on `src/risk/`, `src/execution/`, `src/adapters/`; relaxed elsewhere

#### Hard Limits (Ready for Enforcement in Phase 4)
Config keys defined and ready for risk layer:
- `MAX_NOTIONAL_PER_TRADE` (default 1000.0)
- `MAX_DAILY_LOSS` (default 5000.0)
- `MAX_DAILY_DRAWDOWN_PERCENT` (default 10.0)
- `MAX_CONCURRENT_POSITIONS` (default 5)
- `ORDER_COOLDOWN_SECONDS` (default 5.0)

---

## Phase 1 Test Run (Expected)

```bash
# After setup
cp .env.example .env
python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install -e ".[dev,test]"

# Run Phase 1
python -m src.main
```

**Expected output**:
```
================================================================================
Crypto Algo Trading Agent Starting
================================================================================
[2026-06-20 10:30:45] INFO     src.main: DRY_RUN=true — no live trades will be executed
[2026-06-20 10:30:45] INFO     src.main: Max notional per trade: $1000.0
[2026-06-20 10:30:45] INFO     src.main: Max daily loss: $5000.0 (10.0% of equity)
[2026-06-20 10:30:45] INFO     src.main: Max concurrent positions: 5
[2026-06-20 10:30:45] INFO     src.main: Order cooldown: 5.0s
[2026-06-20 10:30:45] INFO     src.main: Configuration loaded, logging initialized
[2026-06-20 10:30:45] INFO     src.main: Ready for Phase 2: Exchange Adapters
```

Logs also written to `logs/trading_agent.log` in JSON format.

---

## Phase 2 — Exchange Adapters (IN PROGRESS)

### Status / What’s been implemented

#### New Phase 2 adapter scaffolding (safe dry-run contract only)
- **`src/adapters/base.py`**
  - `ExchangeAdapter` ABC (async contract) + shared dataclasses:
    `Ticker`, `OHLCVBar`, `Balance`, `OrderResult`, `Position`
  - adapter error types: `AdapterError`, `AdapterConnectionError`, `AdapterDataError`, `AdapterOrderError`
- **`src/adapters/ccxt_adapter.py`**
  - `CCXTAdapter` implementing the ABC
  - **dry_run=True** returns deterministic placeholder data (no network)
  - **dry_run=False** raises `NotImplementedError` (Phase 2 live integration next)
- **`src/adapters/solana_adapter.py`**
  - `SolanaDEXAdapter` implementing the ABC
  - **dry_run=True** returns deterministic placeholder data (no network)
  - **dry_run=False** raises `NotImplementedError` (Phase 2 live integration next)
- **`src/adapters/__init__.py`**
  - exports the adapter classes + shared dataclasses/errors

#### New contract tests (no live network calls)
- **`tests/test_adapters_contract.py`**
  - verifies required methods are async/awaitable
  - verifies dry-run return types/shapes for:
    `get_ticker`, `get_ohlcv`, `get_balance`, `place_order`, `cancel_order`, `get_open_positions`

#### Testing status (updated)
- Installed test extras and executed pytest successfully:
  - **`python -m pytest -q`**
  - **Result: 4 passed** (`tests/test_adapters_contract.py`)

### Planned Implementation (next)

1. **`src/adapters/base.py`**:
   - `ExchangeAdapter` abstract base class (ABC)
   - Core async methods:
     - `get_ticker(symbol)` → current bid/ask/last
     - `get_ohlcv(symbol, timeframe, limit)` → historical OHLCV
     - `get_balance()` → account balances
     - `place_order(symbol, side, order_type, amount, price)` → order ID
     - `cancel_order(symbol, order_id)` → confirmation
     - `get_open_positions()` → list of open trades
     - (Additional: `get_position(symbol)`, `close_position(symbol)`)
   - Properties: `exchange_name`, `is_testnet`

2. **Upper-layer Market Structure Signals (Phase 3.5+)**
   - Add a venue-agnostic “market structure” signal layer that sits above strategies:
     - **FVG (Fair Value Gap)** detection + mitigation rules (how/when price re-enters)
     - **Order Block** identification (bullish/bearish OB zones) + invalidation logic
     - **BGV / Break & Guard Volume** concepts (volume-guarded breakout regimes)
     - **Liquidity swap** modeling (liquidity grabs → impulse regime)
   - Technical factors to improve efficiency:
     - Precompute rolling pivots/swing structure on OHLCV cache (Parquet) to avoid O(N²)
     - Use vectorized calculations where possible; keep upper-layer pure + deterministic
     - Normalize timezones and align candle boundaries across adapters/backtests
     - Parameterize thresholds (gap size, OB overlap %, liquidity-sweep confirmation bars)
     - Add “signal confidence” score so risk/execution can filter low-quality setups

3. **Crypto Algo Trading KPIs (Phase 3.5+)**
   - Extend backtest outputs + future dashboard/MCP queries with core KPIs:
     - **Win rate**, **profit factor**, **expectancy (avg R)**, **average win/loss**
     - **Max drawdown** (absolute + %), **Sharpe/Sortino** (if enough returns series)
     - **Calmar ratio**, **return / maxDD**
     - **Trade count**, **exposure time**, **turnover**
     - **Slippage sensitivity** (simulated fill assumptions)
     - **Kill-switch frequency** + breach counts (risk-system KPI)
     - **Latency proxy** (bar→signal→fill steps in simulation)
     - **FVG/OB/Liquidity-swap hit-rate**: structure → profitable follow-through
     - **Signal precision/recall proxy**: setup → outcome mapping for tuning

4. **`src/adapters/ccxt_adapter.py`**:
   - `CCXTAdapter(ExchangeAdapter)` implementing ABC
   - Constructor: exchange name (e.g., "binance"), API key/secret, testnet flag
   - Uses `ccxt` library under the hood; maps ccxt methods to ExchangeAdapter interface
   - Error handling for network/API errors
   - Testnet detection & configuration (Binance spot via ccxt `defaultType=spot`)

5. **`src/adapters/solana_adapter.py`**:
   - `SolanaDEXAdapter(ExchangeAdapter)` implementing ABC
   - Constructor: Helius RPC URL, wallet (Keypair), commitment level
   - Uses `solana-py` + `httpx` for Helius RPC + Jupiter API
   - Maps to ExchangeAdapter interface:
     - `get_ticker()` → Jupiter price quote API
     - `get_ohlcv()` → Birdeye API (or fallback to local Parquet cache)
     - `get_balance()` → Solana account query (SOL + token balances)
     - `place_order()` → Jupiter swap API + transaction signing
     - `cancel_order()` → tx cancellation (if applicable)
     - `get_open_positions()` → on-chain position/liquidity data (if applicable)
   - Handles signing, RPC rate limits, and confirmation

6. **`tests/test_adapters_ccxt.py`**:
   - Functional tests against Binance testnet (or mock where no credentials)
   - Test each method: get_ticker, get_ohlcv, get_balance, place_order (dry), cancel_order
   - Fixtures for mock data
   - Assert interface contract (correct return types/fields)

7. **`tests/test_adapters_solana.py`**:
   - Functional tests against Solana devnet (or mock where no credentials)
   - Similar structure to CCXT tests
   - Uses devnet wallet (funded via faucet/airdrop)
   - Test token swaps via Jupiter
   - Assert interface contract

### Key Design Decisions for Phase 2
- **Single ABC interface** ensures strategy/risk layers are venue-blind
- **async/await throughout** for non-blocking I/O
- **Error handling**: Raise custom exceptions (e.g., `AdapterError`, `InsufficientBalance`)
- **Type hints**: Full typing on all public methods
- **Testnet-first**: Both adapters default to testnet/devnet
- **No caching in adapters** (caching handled by backtest/data layer)

---

## Current State & Next Steps

### What's Working
✅ Configuration system (pydantic-settings)
✅ Logging (dual handlers: JSON file + console)
✅ Project structure (all folders created)
✅ Dependencies (pyproject.toml complete)
✅ Documentation (README with checklist and diagrams)
✅ Hard limits defined in config (ready for Phase 4 enforcement)

### What's Next (Phase 2)
⏳ Exchange adapter ABC & CCXT/Solana implementations
⏳ Integration tests against real sandbox endpoints
⏳ Backtest data caching (OHLCV → Parquet)

### Checklist Before Phase 2
- [ ] Review Phase 0 & Phase 1 completions above
- [ ] Confirm no changes needed to architecture or config schema
- [ ] Ready to proceed? Say "continue" for Phase 2

---

## Important Notes for Future Sessions

### Continuing This Project
1. Open `Crypto_Algo_Trading_Agent/CLAUDE.md` — it contains the full seed prompt for continuity
2. Reference this `chat.md` file for Phase 0 decisions and Phase 1 completions
3. Load `CLAUDE.md` in Claude Code as persistent context (reads automatically)
4. Always work phase-by-phase — don't skip ahead or bulk-generate

### Hard Limits (Non-Negotiable)
These are built into config, ready for enforcement in Phase 4:
- **DRY_RUN** defaults true; live requires two gates
- **MAX_NOTIONAL_PER_TRADE**: hard cap before any order
- **MAX_DAILY_LOSS** & **MAX_DAILY_DRAWDOWN_PERCENT**: auto kill-switch
- **MAX_CONCURRENT_POSITIONS**: rejects signals exceeding limit
- **Stop-loss requirement**: every live position must define one
- **ORDER_COOLDOWN_SECONDS**: rate limit between orders
- **Kill switch**: testable via dedicated unit test

### Design Principles (Keep Sacred)
1. **Claude advisory is async & read-only** — never in the hot path
2. **Risk/execution layer is deterministic** — no LLM calls in order placement
3. **MCP server is separate process** — isolated from execution loop
4. **Logging is dual-handler** — JSON for parsing, console for dev
5. **Config via pydantic-settings** — no hardcoded keys, .env template provided
6. **Type hints on critical paths** — mypy strict on risk/, execution/, adapters/

### File Tree (For Reference)
```
crypto_algo_trading_agent/
├── src/
│   ├── adapters/           (Phase 2: CCXT, Solana adapters)
│   ├── strategies/         (Phase 3: MA crossover, RSI strategies)
│   ├── risk/               (Phase 4: hard limits, kill switch)
│   ├── execution/          (Phase 4: order placement, rule-based)
│   ├── backtest/           (Phase 3: engine, historical data)
│   ├── advisory/           (Phase 5: Claude advisor, MCP server)
│   ├── data/               (Phase 2+: DB models, OHLCV cache)
│   ├── notifications/      (Phase 6: Telegram, webhooks)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── main.py
│   ├── logging_setup.py
│   └── __init__.py
├── tests/                  (Phase 2+: pytest suite)
├── pyproject.toml
├── .env.example
├── .gitignore
├── CLAUDE.md               (← Persistent seed prompt)
├── README.md
└── chat.md                 (← This file)
```

---

**Session complete. Ready for Phase 2?**
