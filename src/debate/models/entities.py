"""Data entity models for debate arguments, scores, and results."""

import logging

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
    gaps_identified: list[str] | None = None
    acknowledged_valid_points: list[str] | None = None  # Valid opponent points acknowledged
    identified_weaknesses: list[str] | None = None  # Weaknesses found in opponent's argument

    def to_dict(self) -> dict:
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

    def to_dict(self) -> dict:
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
    debater_name: str | None = None  # Who failed to meet standards
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()

    def __str__(self) -> str:
        """String representation."""
        return f"Debate {'terminated' if self.terminated else 'completed'}: {self.reason} at Round {self.round_number}"


class ReflectiveAnalysis(BaseModel):
    """Debater's reflection on the session."""

    learned: list[str] = Field(default_factory=list, description="What was learned from the opponent")
    weaknesses: list[str] = Field(default_factory=list, description="Self-identified weaknesses in arguments")
    corrections: list[str] = Field(default_factory=list, description="How those weaknesses were corrected")


class Baseline(BaseModel):
    """Single-agent control group data for scientific comparison."""

    content: str
    score: Score


class DebateResult(BaseModel):
    """Complete result of a debate session."""

    topic: str
    arguments: list[Argument]
    scores: list[Score]
    winner: str | None = None
    timestamp: str
    num_rounds: int
    participants: dict[str, str]  # {name: role}
    termination: DebateTermination | None = None  # Why debate ended
    participant_summaries: dict[str, str] | None = None  # {name: summary}
    reflective_analysis: dict[str, ReflectiveAnalysis] | None = None  # {name: analysis}
    baseline: Baseline | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return self.model_dump()

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=indent)

    def save(self, filepath: str) -> None:
        """Save debate result to JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())
        logger.info(f"Debate result saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "DebateResult":
        """Load debate result from JSON file."""
        with open(filepath) as f:
            return cls.model_validate_json(f.read())


class GapAnalysis(BaseModel):
    """Result of opponent's argument analysis."""

    gaps: list[str] = Field(default_factory=list)
    inconsistencies: list[str] = Field(default_factory=list)
    logical_fallacies: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

    def all_weaknesses(self) -> list[str]:
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
    missing_elements: list[str] = Field(default_factory=list)


class OpponentEvaluation(BaseModel):
    """Debater's evaluation of opponent's points."""

    acknowledged_valid_points: list[str] = Field(default_factory=list)
    identified_weaknesses: list[str] = Field(default_factory=list)
