"""Data models for the debate platform."""

from .config import DebateConfig
from .entities import (
    Argument,
    Baseline,
    DebateResult,
    DebateTermination,
    GapAnalysis,
    OpponentEvaluation,
    ReflectiveAnalysis,
    Score,
    ValidationResult,
)

__all__ = [
    "DebateConfig",
    "Argument",
    "Score",
    "DebateTermination",
    "DebateResult",
    "ValidationResult",
    "GapAnalysis",
    "OpponentEvaluation",
    "ReflectiveAnalysis",
    "Baseline",
]
