# Crypto Algo Trading Agent — Claude Code Seed Prompt

**How to use this file**

1. Open your `Crypto_Algo_Trading_Agent` folder in VS Code.

2. Save this whole file as `CLAUDE.md` in the project root — Claude Code reads it automatically as persistent context every session.

3. Open Claude Code in the integrated terminal and paste the contents of **Section A** as your first message to kick off Phase 0.

4. Work phase by phase. Don't let it bulk-generate everything at once — review the diff after each phase before saying "continue."

---

## Section A — paste this into Claude Code

```
You are building a crypto algorithmic trading agent skeleton with me. This is a
real project, not a toy — but every API key starts empty, and live trading is
gated behind explicit hard limits defined below. Work in phases. After each
phase, stop, summarize what you built, and wait for me to say "continue"
before moving on. Do not skip ahead or generate every file in one shot.

## Architecture

- Language: Python 3.11+, fully typed (mypy-clean), async-first (asyncio) for
  the execution loop.
- Exchange abstraction: a single ExchangeAdapter ABC (get_ticker, get_ohlcv,
  get_balance, place_order, cancel_order, get_open_positions). Two concrete
  adapters:
  - CCXTAdapter — wraps the ccxt library for centralized exchanges
    (Binance, Bybit, etc.)
  - SolanaDEXAdapter — wraps Jupiter's swap API + solana-py for on-chain DEX
    trades (pump.fun-graduated tokens, Raydium pairs)
  Both must satisfy the same interface so the strategy/risk/execution layers
  never know which venue they're talking to.
- Strategy layer: pluggable Strategy base class. Ship two reference
  strategies only (moving-average crossover, RSI mean-reversion) — these are
  scaffolding examples, not advice on what to actually trade.
- Risk & execution layer: deterministic, rule-based. This is what actually
  places orders. No LLM call sits in this path.
- Claude advisory layer: a separate, async, non-blocking module that reviews
  backtest results and strategy code and proposes parameter changes or flags
  anomalies. It writes suggestions to a review queue — it never calls
  place_order directly. Wire it through an MCP server (reference the
  ccxt-mcp / Trade-With-Claude/cbt-framework patterns) so market data and
  backtests are also queryable from inside Claude Code during development.
- Persistence: SQLite to start (swappable for Postgres later) for the trade
  ledger, equity curve, and advisory review queue.
- Config: pydantic-settings reading from .env. Generate .env.example with
  every key present but empty. .env itself goes in .gitignore — never write
  real keys anywhere in the repo.

## Hard limits (non-negotiable — build these into the risk layer, not the UI)

- DRY_RUN defaults to true. Flipping to live requires both an env var AND a
  typed confirmation string at startup — two separate gates.
- Max notional per trade: hard cap, config-driven, enforced in code before
  any place_order call, not just documented.
- Max daily loss / drawdown: auto-trips a kill switch that halts new orders
  and alerts me (stub a Telegram/webhook notifier) when breached.
- Max concurrent open positions: hard cap.
- Every live position must carry a stop-loss order; reject any strategy
  signal that doesn't define one.
- Cooldown/rate limit between orders to prevent runaway loops on a bad signal.
- Kill switch must be testable with a dedicated unit test that actually halts
  execution, not just a flag check.

## Folder structure (propose this, confirm with me before scaffolding)

crypto_algo_trading_agent/
  adapters/
  strategies/
  risk/
  execution/
  backtest/
  advisory/        # Claude-facing module + MCP server
  data/             # OHLCV cache, trade ledger
  notifications/
  config/
  tests/
  CLAUDE.md
  .env.example
  pyproject.toml

## Phases — work through these one at a time, pausing for my review after each

0. Confirm architecture and folder structure with me. Ask clarifying
   questions now, before writing code.
1. Scaffold the repo: pyproject.toml, folder structure, .env.example, config
   loader, logging setup, README.
2. Build the exchange adapter layer and the abstract interface. Stub both
   adapters against a public sandbox/testnet endpoint where one exists.
3. Build the backtesting engine and the two reference strategies. Prove it
   works against historical OHLCV data you fetch and cache locally.
4. Build the risk and execution layer with every hard limit above enforced
   in code, with unit tests for each limit — especially the kill switch.
5. Build the Claude advisory module and the MCP server wrapping it, so
   backtests and market data are queryable from Claude Code directly.
6. Add notifications (trade fills, kill-switch trips, errors) and a minimal
   CLI to check status/positions/PnL.
7. Write tests (80%+ coverage on the risk/execution layer specifically) and
   do a docs pass — README with setup steps, a mermaid architecture diagram,
   and a "going live" checklist.

Ask me before adding any new dependency that isn't already listed above.
```

---

## Section B — notes for you (not part of the Claude Code prompt)

- **Why CCXT plus a separate Solana adapter, not CCXT alone.** CCXT covers
100+ centralized exchanges well but doesn't natively do Solana AMM swaps
(Jupiter/Raydium). The shared ExchangeAdapter interface is what actually
gives you the exchange-agnostic property — the strategy and risk layers
stay venue-blind.

- **Why Claude stays out of the hot path.** With live trading from day one,
the order-placement logic needs to be deterministic and fully unit-testable.
An LLM call per tick adds latency, cost, and a non-deterministic failure
mode exactly where you can least afford one. The advisory pattern (Claude
reviews backtests/strategy code async, the rule engine or you approves)
gets you the reasoning benefit without an LLM sitting between a signal and
an order.

- **Reusing your HITL pattern.** The human-in-the-loop approval gate from
your Agentic Infrastructure Blueprint project slots in cleanly here as an
optional gate on trades above a notional threshold — worth wiring in once
the core loop is stable.

- **Worth a glance before Phase 0**: `Trade-With-Claude/cbt-framework` on
GitHub (a Claude-Code-native backtest-to-live workflow), Freqtrade's
dry-run/strategy-plugin architecture, and the `ccxt-mcp` server for the
MCP tool-calling pattern.

- **On "live trading from day one."** The hard limits above are designed so
that's genuinely workable: DRY_RUN defaults on, live mode needs two
deliberate gates, every position carries a stop-loss by construction.
Start with the smallest notional cap you can stand to lose completely
while you watch it run for the first week or two. Not financial advice —
just standard practice for anything touching real capital on its first run.
