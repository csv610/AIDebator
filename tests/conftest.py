import pytest
from unittest.mock import AsyncMock, MagicMock
from src.debate.participants import Organizer, Debater, Judge
from src.debate.models import Score, ReflectiveAnalysis


@pytest.fixture
def mock_organizer():
    org = MagicMock(spec=Organizer)
    org.name = "Organizer"
    org.get_role.return_value = "organizer"
    org.generate_overview = AsyncMock(return_value="Neutral overview of the topic covering both sides.")
    org.count_words.return_value = 10
    return org


@pytest.fixture
def mock_score_supporter():
    return Score(
        debater_role="supporter", argument_quality=8.0, evidence_quality=8.0,
        logical_consistency=8.0, responsiveness_to_gaps=8.0, overall_score=8.0, feedback="Good"
    )


@pytest.fixture
def mock_score_opposer():
    return Score(
        debater_role="opposer", argument_quality=7.0, evidence_quality=7.0,
        logical_consistency=7.0, responsiveness_to_gaps=7.0, overall_score=7.0, feedback="Okay"
    )


@pytest.fixture
def mock_reflective_analysis():
    return ReflectiveAnalysis(
        learned=["Learned new perspective"],
        weaknesses=["Weak evidence in round 1"],
        corrections=["Added citations in round 2"]
    )


def _make_mock_debater(name, role, reflective_analysis):
    d = MagicMock(spec=Debater)
    d.name = name
    d.is_supporter = (role == "supporter")
    d.get_role.return_value = role
    d.generate_argument = AsyncMock(return_value=f"{name} argument")
    d.validate_argument_quality = AsyncMock(return_value=(True, "Valid"))
    d.evaluate_opponent_argument = AsyncMock(return_value=(["Valid Point"], ["Weakness"]))
    d.analyze_opponent_arguments = AsyncMock(return_value=["Gap"])
    d.generate_summary = AsyncMock(return_value=f"{name} summary")
    d.generate_reflective_analysis = AsyncMock(return_value=reflective_analysis)
    d.count_words.return_value = 10
    return d


@pytest.fixture
def mock_supporter(mock_reflective_analysis):
    return _make_mock_debater("Supporter", "supporter", mock_reflective_analysis)


@pytest.fixture
def mock_opposer(mock_reflective_analysis):
    return _make_mock_debater("Opposer", "opposer", mock_reflective_analysis)


@pytest.fixture
def mock_judge(mock_score_supporter, mock_score_opposer):
    jdg = MagicMock(spec=Judge)
    jdg.name = "Judge"
    jdg.get_role.return_value = "judge"
    jdg.score_debate = AsyncMock(return_value=[mock_score_supporter, mock_score_opposer])
    jdg.generate_baseline = AsyncMock(return_value="Baseline analysis")
    jdg.evaluate_baseline_score = AsyncMock(return_value=mock_score_supporter)
    return jdg
