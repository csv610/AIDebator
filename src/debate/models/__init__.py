"""Data models for the debate platform."""

from .config import DebateConfig
from .entities import Argument, Score, DebateTermination, DebateResult

__all__ = [
    "DebateConfig",
    "Argument",
    "Score",
    "DebateTermination",
    "DebateResult",
]
