import pytest
from src.debate import DebateSession, DebateConfig, DebateResult
from src.debate.participants import Organizer, Debater, Judge


@pytest.mark.asyncio
async def test_full_debate_flow_with_mocks(mock_organizer, mock_supporter, mock_opposer, mock_judge):
    """End-to-end integration test with mocked participants."""
    session = DebateSession(
        topic="Test Topic",
        organizer=mock_organizer,
        supporter=mock_supporter,
        opposer=mock_opposer,
        judge=mock_judge
    )

    result = await session.run(num_rounds=3)

    assert isinstance(result, DebateResult)
    assert result.topic == "Test Topic"
    assert len(result.arguments) == 7  # Organizer + 3 rounds x 2 debaters
    assert len(result.scores) == 2
    assert result.num_rounds == 3
    assert not result.termination.terminated
    assert result.baseline is not None
    assert result.winner is not None
    assert result.participant_summaries is not None
    assert result.reflective_analysis is not None

    mock_organizer.generate_overview.assert_called_once()
    assert mock_supporter.generate_argument.call_count == 3
    assert mock_opposer.generate_argument.call_count == 3
    assert mock_judge.score_debate.call_count == 3  # intermediate rounds 2+3 + final

    # Verify argument ordering
    assert result.arguments[0].participant_role == "organizer"
    assert result.arguments[0].round_number == 0

    for i in range(3):
        supporter_arg = result.arguments[1 + i * 2]
        opposer_arg = result.arguments[2 + i * 2]
        assert supporter_arg.participant_role == "supporter"
        assert opposer_arg.participant_role == "opposer"
        assert supporter_arg.round_number == i + 1
        assert opposer_arg.round_number == i + 1


@pytest.mark.asyncio
async def test_from_config_creates_session_with_dict(mock_judge):
    """Verify DebateSession.from_config accepts both dict and DebateConfig."""
    config_dict = {
        "topic": "Test",
        "organizer_model": "gpt-4",
        "supporter_model": "gpt-4",
        "opposer_model": "gpt-4",
        "judge_model": "gpt-4",
        "num_rounds": 2,
    }
    config_obj = DebateConfig.model_validate(config_dict)

    session_from_dict = DebateSession.from_config(config_dict)
    session_from_obj = DebateSession.from_config(config_obj)

    assert session_from_dict.topic == "Test"
    assert session_from_obj.topic == "Test"


@pytest.mark.asyncio
async def test_debate_serialization_roundtrip(mock_organizer, mock_supporter, mock_opposer, mock_judge):
    """Verify DebateResult to_dict, to_json, save and load round-trip correctly."""
    import json, tempfile

    session = DebateSession(
        topic="Test Topic",
        organizer=mock_organizer,
        supporter=mock_supporter,
        opposer=mock_opposer,
        judge=mock_judge
    )

    result = await session.run(num_rounds=1)

    # Dict round-trip
    d = result.to_dict()
    restored = DebateResult.model_validate(d)
    assert restored.topic == result.topic
    assert restored.winner == result.winner

    # JSON round-trip
    j = result.to_json()
    parsed = json.loads(j)
    assert parsed["topic"] == "Test Topic"

    # File round-trip
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        fname = f.name
    try:
        result.save(fname)
        loaded = DebateResult.load(fname)
        assert loaded.topic == result.topic
        assert loaded.winner == result.winner
    finally:
        import os
        os.unlink(fname)
