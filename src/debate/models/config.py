"""Configuration models for debate sessions."""

from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator


class DebateConfig(BaseModel):
    """Configuration for a debate session."""
    topic: str = Field(..., min_length=1, description="The debate topic")
    organizer_model: str = Field(..., min_length=1, description="LLM model for organizer")
    supporter_model: str = Field(..., min_length=1, description="LLM model for supporter")
    supporter_persona: Optional[str] = Field(None, description="Expert persona for the supporter")
    opposer_model: str = Field(..., min_length=1, description="LLM model for opposer")
    opposer_persona: Optional[str] = Field(None, description="Expert persona for the opposer")
    judge_model: str = Field(..., min_length=1, description="LLM model for judge")
    num_rounds: int = Field(default=3, ge=1, le=10, description="Number of debate rounds (1-10)")

    @field_validator("topic", "organizer_model", "supporter_model", "opposer_model", "judge_model")
    @classmethod
    def not_empty_string(cls, v: str) -> str:
        """Validate that strings are not just whitespace."""
        if not v.strip():
            raise ValueError("String cannot be empty or only whitespace")
        return v.strip()

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.model_dump()
