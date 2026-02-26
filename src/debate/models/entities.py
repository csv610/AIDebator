"""Data entity models for debate arguments, scores, and results."""

import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Argument(BaseModel):
    """Represents a single argument in the debate."""
    round_number: int
    participant_name: str
    participant_role: str  # "organizer", "supporter", "opposer"
    content: str
    timestamp: str
    word_count: int
    gaps_identified: Optional[List[str]] = None
    acknowledged_valid_points: Optional[List[str]] = None  # Valid opponent points acknowledged
    identified_weaknesses: Optional[List[str]] = None  # Weaknesses found in opponent's argument

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.model_dump()

    def __str__(self) -> str:
        """String representation."""
        return f"{self.participant_name} (Round {self.round_number}): {self.content[:100]}..."


class Score(BaseModel):
    """Score breakdown for a single debater."""
    debater_role: str  # "supporter" or "opposer"
    argument_quality: float = Field(ge=0, le=10)
    evidence_quality: float = Field(ge=0, le=10)
    logical_consistency: float = Field(ge=0, le=10)
    responsiveness_to_gaps: float = Field(ge=0, le=10)
    overall_score: float = Field(ge=0, le=10)
    feedback: str
    fact_count: int = 0  # Number of facts/citations used
    irrefutable_arguments: int = 0  # Number of evidence-backed arguments

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.model_dump()

    def __str__(self) -> str:
        """String representation."""
        return f"{self.debater_role}: {self.overall_score:.1f}/10 ({self.fact_count} facts, {self.irrefutable_arguments} backed arguments)"


class DebateTermination(BaseModel):
    """Reason for debate termination."""
    terminated: bool
    reason: str  # "completed", "low_quality", "no_new_info", "no_refutation", "max_rounds"
    round_number: int
    debater_name: Optional[str] = None  # Who failed to meet standards
    message: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.model_dump()

    def __str__(self) -> str:
        """String representation."""
        return f"Debate {'terminated' if self.terminated else 'completed'}: {self.reason} at Round {self.round_number}"


class ReflectiveAnalysis(BaseModel):
    """Debater's reflection on the session."""
    learned: List[str] = Field(default_factory=list, description="What was learned from the opponent")
    weaknesses: List[str] = Field(default_factory=list, description="Self-identified weaknesses in arguments")
    corrections: List[str] = Field(default_factory=list, description="How those weaknesses were corrected")


class DebateResult(BaseModel):
    """Complete result of a debate session."""
    topic: str
    arguments: List[Argument]
    scores: List[Score]
    winner: Optional[str] = None
    timestamp: str
    num_rounds: int
    participants: Dict[str, str]  # {name: role}
    termination: Optional[DebateTermination] = None  # Why debate ended
    participant_summaries: Optional[Dict[str, str]] = None  # {name: summary}
    reflective_analysis: Optional[Dict[str, ReflectiveAnalysis]] = None  # {name: analysis}

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)

    def save(self, filepath: str) -> None:
        """Save debate result to JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
        logger.info(f"Debate result saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'DebateResult':
        """Load debate result from JSON file."""
        with open(filepath, 'r') as f:
            return cls.model_validate_json(f.read())


class GapAnalysis(BaseModel):
    """Result of opponent's argument analysis."""
    gaps: List[str] = Field(default_factory=list)
    inconsistencies: List[str] = Field(default_factory=list)
    logical_fallacies: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)

    def all_weaknesses(self) -> List[str]:
        """Return a combined list of all identified weaknesses."""
        return self.gaps + self.inconsistencies + self.logical_fallacies


class ValidationResult(BaseModel):
    """Result of argument quality validation."""
    has_new_information: bool
    has_strong_novelty: bool
    refutes_opponent: bool
    avoids_repetition: bool
    is_substantive: bool
    reason: str
    missing_elements: List[str] = Field(default_factory=list)


class OpponentEvaluation(BaseModel):
    """Debater's evaluation of opponent's points."""
    acknowledged_valid_points: List[str] = Field(default_factory=list)
    identified_weaknesses: List[str] = Field(default_factory=list)
