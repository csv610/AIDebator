"""AI Debate Platform - Multi-participant academic debate orchestration with evidence-based scoring."""

from .models import DebateConfig, Argument, Score, DebateTermination, DebateResult
from .participants import Participant, Organizer, Debater, Judge
from .engine import DebateSession

__version__ = "1.0.0"

__all__ = [
    "DebateConfig",
    "Argument",
    "Score",
    "DebateTermination",
    "DebateResult",
    "Participant",
    "Organizer",
    "Debater",
    "Judge",
    "DebateSession",
]
