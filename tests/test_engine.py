import pytest
from unittest.mock import MagicMock
from src.debate.engine.session import DebateSession
from src.debate.models import Score


@pytest.mark.asyncio
async def test_session_run_completes(mock_organizer, mock_supporter, mock_opposer, mock_judge):
    session = DebateSession(
        topic="Test Topic",
        organizer=mock_organizer,
        supporter=mock_supporter,
        opposer=mock_opposer,
        judge=mock_judge
    )

    result = await session.run(num_rounds=1)

    assert result.topic == "Test Topic"
    assert len(result.arguments) == 3
    assert len(result.scores) == 2
    assert result.winner == "supporter"
    assert not result.termination.terminated
    assert result.baseline is not None
    assert result.baseline.content == "Baseline analysis"

    mock_organizer.generate_overview.assert_called_once()
    assert mock_supporter.generate_argument.call_count == 1
    assert mock_opposer.generate_argument.call_count == 1
    mock_judge.score_debate.assert_called()


@pytest.mark.asyncio
async def test_session_early_termination(mock_organizer, mock_supporter, mock_opposer, mock_judge):
    mock_supporter.validate_argument_quality.side_effect = [(False, "Repetitive")]

    session = DebateSession(
        topic="Test Topic",
        organizer=mock_organizer,
        supporter=mock_supporter,
        opposer=mock_opposer,
        judge=mock_judge
    )

    result = await session.run(num_rounds=2)

    assert result.termination.terminated
    assert result.termination.reason == "low_quality"
    assert result.termination.round_number == 2
    assert result.termination.debater_name == "Supporter"
    assert result.num_rounds == 2


class TestDetermineWinner:
    """Unit tests for _determine_winner logic."""

    def make_session(self):
        return DebateSession("Topic", MagicMock(), MagicMock(), MagicMock(), MagicMock())

    def test_supporter_wins(self):
        scores = [
            Score(debater_role="supporter", argument_quality=9, evidence_quality=9,
                  logical_consistency=9, responsiveness_to_gaps=9, overall_score=9.0, feedback=""),
            Score(debater_role="opposer", argument_quality=8, evidence_quality=8,
                  logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback=""),
        ]
        assert self.make_session()._determine_winner(scores) == "supporter"

    def test_tie(self):
        scores = [
            Score(debater_role="supporter", argument_quality=8, evidence_quality=8,
                  logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback=""),
            Score(debater_role="opposer", argument_quality=8, evidence_quality=8,
                  logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback=""),
        ]
        assert self.make_session()._determine_winner(scores) is None

    def test_opposer_wins(self):
        scores = [
            Score(debater_role="supporter", argument_quality=7, evidence_quality=7,
                  logical_consistency=7, responsiveness_to_gaps=7, overall_score=7.0, feedback=""),
            Score(debater_role="opposer", argument_quality=9, evidence_quality=9,
                  logical_consistency=9, responsiveness_to_gaps=9, overall_score=9.0, feedback=""),
        ]
        assert self.make_session()._determine_winner(scores) == "opposer"

    def test_less_than_two_scores_returns_none(self):
        scores = [
            Score(debater_role="supporter", argument_quality=8, evidence_quality=8,
                  logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback=""),
        ]
        assert self.make_session()._determine_winner(scores) is None

    def test_empty_scores_returns_none(self):
        assert self.make_session()._determine_winner([]) is None
