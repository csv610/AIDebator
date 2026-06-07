import json
import pytest
from unittest.mock import AsyncMock, patch
from src.debate.participants import Organizer, Debater, Judge
from src.debate.models import Argument, ValidationResult, Score


@pytest.mark.asyncio
async def test_organizer_generate_overview():
    org = Organizer("TestOrg", "gpt-4")
    with patch.object(Organizer, 'generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Overview content"
        overview = await org.generate_overview("Topic")
        assert overview == "Overview content"


@pytest.mark.asyncio
async def test_debater_generate_argument():
    debater = Debater("TestDebater", "gpt-4", is_supporter=True)
    with patch.object(Debater, 'generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Argument content"
        arg = await debater.generate_argument("Topic", 1, is_initial=True)
        assert arg == "Argument content"


@pytest.mark.asyncio
async def test_debater_validate_quality():
    debater = Debater("TestDebater", "gpt-4", is_supporter=True)
    mock_val = ValidationResult(
        has_new_information=True, has_strong_novelty=True, refutes_opponent=False,
        avoids_repetition=True, is_substantive=True, reason="Good"
    )

    with patch.object(Debater, 'generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_val.model_dump_json()

        is_valid, reason = await debater.validate_argument_quality("Topic", "Short arg")
        assert not is_valid
        assert "too short" in reason

        long_arg = "word " * 60
        is_valid, reason = await debater.validate_argument_quality("Topic", long_arg)
        assert is_valid
        assert reason == "Good"


@pytest.mark.asyncio
async def test_judge_scoring():
    judge = Judge("TestJudge", "gpt-4")
    mock_score_data = {
        "debater_role": "supporter", "argument_quality": 8.0, "evidence_quality": 9.0,
        "logical_consistency": 8.5, "responsiveness_to_gaps": 7.0, "overall_score": 8.3,
        "fact_count": 4, "irrefutable_arguments": 2, "feedback": "Strong evidence."
    }

    with patch.object(Judge, 'generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = json.dumps(mock_score_data)
        args = [
            Argument(round_number=1, participant_name="S", participant_role="supporter",
                     content="C", timestamp="T", word_count=1)
        ]
        scores = await judge.score_debate("Topic", args)
        assert len(scores) == 1
        assert scores[0].overall_score == 8.3
        assert scores[0].debater_role == "supporter"


class TestDynamicAdjustments:

    def make_judge(self):
        return Judge("TestJudge", "gpt-4")

    def test_bonus_for_valid_points(self):
        judge = self.make_judge()
        base = Score(debater_role="supporter", argument_quality=8, evidence_quality=8,
                     logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback="Base")
        args = [
            Argument(round_number=1, participant_name="Opposer", participant_role="opposer",
                     content="C", timestamp="T", word_count=1,
                     acknowledged_valid_points=["Point"], identified_weaknesses=[])
        ]
        adjusted = judge._apply_dynamic_adjustments(base, "supporter", args)
        assert adjusted.overall_score == 8.15

    def test_penalty_for_weaknesses(self):
        judge = self.make_judge()
        base = Score(debater_role="supporter", argument_quality=8, evidence_quality=8,
                     logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback="Base")
        args = [
            Argument(round_number=1, participant_name="Opposer", participant_role="opposer",
                     content="C", timestamp="T", word_count=1,
                     acknowledged_valid_points=[], identified_weaknesses=["Weakness"])
        ]
        adjusted = judge._apply_dynamic_adjustments(base, "supporter", args)
        assert adjusted.overall_score == 7.9

    def test_bonus_and_penalty_combined(self):
        judge = self.make_judge()
        base = Score(debater_role="supporter", argument_quality=8, evidence_quality=8,
                     logical_consistency=8, responsiveness_to_gaps=8, overall_score=8.0, feedback="Base")
        args = [
            Argument(round_number=1, participant_name="Opposer", participant_role="opposer",
                     content="C", timestamp="T", word_count=1,
                     acknowledged_valid_points=["Point"], identified_weaknesses=["Weakness"])
        ]
        adjusted = judge._apply_dynamic_adjustments(base, "supporter", args)
        assert round(adjusted.overall_score, 2) == 8.05

    def test_score_capped_at_ten(self):
        judge = self.make_judge()
        base = Score(debater_role="supporter", argument_quality=10, evidence_quality=10,
                     logical_consistency=10, responsiveness_to_gaps=10, overall_score=10.0, feedback="Perfect")
        args = [
            Argument(round_number=1, participant_name="Opposer", participant_role="opposer",
                     content="C", timestamp="T", word_count=1,
                     acknowledged_valid_points=["P1", "P2", "P3"], identified_weaknesses=[])
        ]
        adjusted = judge._apply_dynamic_adjustments(base, "supporter", args)
        assert adjusted.overall_score == 10.0
