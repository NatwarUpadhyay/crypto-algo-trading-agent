from __future__ import annotations

"""
API package.

Note: Do NOT import FastAPI at package import time.
This keeps the project testable in environments where optional web dependencies
(fastapi/uvicorn) are not installed.
"""

__all__ = ["server"]
