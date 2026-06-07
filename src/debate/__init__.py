"""AI Debate Platform - Multi-participant academic debate orchestration with evidence-based scoring."""

from .engine import DebateSession
from .models import Argument, DebateConfig, DebateResult, DebateTermination, Score
from .participants import Debater, Judge, Organizer, Participant

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
