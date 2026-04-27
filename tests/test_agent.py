"""
test_agent.py — Unit tests for the MoodMatcher agentic loop.

All Anthropic API calls are mocked so tests run without an API key.

Run with:
    pytest tests/test_agent.py -v
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from src.agent import MusicAgent, MAX_POSSIBLE_SCORE, CONFIDENCE_THRESHOLD


# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

SAMPLE_SONGS = [
    {
        "id": 1, "title": "Sunrise City", "artist": "Neon Echo",
        "genre": "pop", "mood": "happy", "energy": 0.82,
        "tempo_bpm": 118.0, "valence": 0.84, "danceability": 0.79, "acousticness": 0.18,
    },
    {
        "id": 2, "title": "Midnight Coding", "artist": "LoRoom",
        "genre": "lofi", "mood": "chill", "energy": 0.42,
        "tempo_bpm": 78.0, "valence": 0.56, "danceability": 0.62, "acousticness": 0.71,
    },
    {
        "id": 12, "title": "Bass Drop Arena", "artist": "Voltline",
        "genre": "edm", "mood": "intense", "energy": 0.95,
        "tempo_bpm": 140.0, "valence": 0.52, "danceability": 0.91, "acousticness": 0.03,
    },
    {
        "id": 3, "title": "Storm Runner", "artist": "Voltline",
        "genre": "rock", "mood": "intense", "energy": 0.91,
        "tempo_bpm": 152.0, "valence": 0.48, "danceability": 0.66, "acousticness": 0.10,
    },
    {
        "id": 6, "title": "Spacewalk Thoughts", "artist": "Orbit Bloom",
        "genre": "ambient", "mood": "chill", "energy": 0.28,
        "tempo_bpm": 60.0, "valence": 0.65, "danceability": 0.41, "acousticness": 0.92,
    },
]


@pytest.fixture
def mock_agent():
    """
    Creates a MusicAgent with a mocked Anthropic client and
    the small in-memory catalog above. No API key required.
    """
    with patch("src.agent.anthropic.Anthropic"):
        agent = MusicAgent.__new__(MusicAgent)
        agent.songs = SAMPLE_SONGS
        agent.client = MagicMock()
    return agent


# ---------------------------------------------------------------------------
# STEP 2: ACT tests
# ---------------------------------------------------------------------------

def test_act_returns_top_k_results(mock_agent):
    """act() should return at most k results."""
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy",
             "target_energy": 0.8, "target_valence": 0.8}
    results = mock_agent.act(prefs, k=2)
    assert len(results) <= 2


def test_act_sorts_by_score_descending(mock_agent):
    """act() results must be sorted highest score first."""
    prefs = {"favorite_genre": "edm", "favorite_mood": "intense",
             "target_energy": 0.95, "target_valence": 0.5}
    results = mock_agent.act(prefs, k=5)
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)


def test_act_top_song_matches_genre(mock_agent):
    """The top-scored song should match the requested genre when available."""
    prefs = {"favorite_genre": "edm", "favorite_mood": "intense",
             "target_energy": 0.95, "target_valence": 0.5}
    results = mock_agent.act(prefs, k=5)
    top_song = results[0][0]
    assert top_song["genre"] == "edm"


# ---------------------------------------------------------------------------
# STEP 3: EVALUATE tests
# ---------------------------------------------------------------------------

def test_evaluate_perfect_score_gives_confidence_one(mock_agent):
    """A recommendation with the max possible score should yield confidence = 1.0."""
    recs = [(SAMPLE_SONGS[0], MAX_POSSIBLE_SCORE, ["genre match", "mood match"])]
    confidence, is_confident = mock_agent.evaluate(recs)
    assert confidence == 1.0
    assert is_confident is True


def test_evaluate_low_score_fails_threshold(mock_agent):
    """A very low score should produce confidence below the threshold."""
    recs = [(SAMPLE_SONGS[1], 0.9, ["energy similarity (+0.50)"])]
    confidence, is_confident = mock_agent.evaluate(recs)
    assert confidence < CONFIDENCE_THRESHOLD
    assert is_confident is False


def test_evaluate_empty_list_returns_zero(mock_agent):
    """Empty recommendation list should return 0.0 confidence, not crash."""
    confidence, is_confident = mock_agent.evaluate([])
    assert confidence == 0.0
    assert is_confident is False


def test_evaluate_confidence_is_normalized(mock_agent):
    """Confidence should always be between 0.0 and 1.0."""
    recs = [(SAMPLE_SONGS[2], 3.5, ["genre match"])]
    confidence, _ = mock_agent.evaluate(recs)
    assert 0.0 <= confidence <= 1.0


# ---------------------------------------------------------------------------
# STEP 1: PLAN tests (mocked API)
# ---------------------------------------------------------------------------

def test_plan_parses_valid_json(mock_agent):
    """plan() should return a valid prefs dict when Claude returns good JSON."""
    good_response = json.dumps({
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.4,
        "target_valence": 0.6,
    })
    mock_agent.client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=good_response)]
    )
    prefs = mock_agent.plan("late night study session vibes")
    assert prefs["favorite_genre"] == "lofi"
    assert prefs["favorite_mood"] == "chill"
    assert 0.0 <= prefs["target_energy"] <= 1.0


def test_plan_falls_back_on_bad_json(mock_agent):
    """plan() should return safe fallback prefs if Claude returns invalid JSON."""
    mock_agent.client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="This is not JSON at all.")]
    )
    prefs = mock_agent.plan("something random")
    # Should not crash and should return a valid dict
    assert "favorite_genre" in prefs
    assert "favorite_mood" in prefs
    assert "target_energy" in prefs
    assert "target_valence" in prefs


# ---------------------------------------------------------------------------
# STEP 4: REFINE tests (mocked API)
# ---------------------------------------------------------------------------

def test_refine_returns_adjusted_prefs(mock_agent):
    """refine() should return updated preferences from Claude."""
    refined_response = json.dumps({
        "favorite_genre": "ambient",
        "favorite_mood": "moody",
        "target_energy": 0.3,
        "target_valence": 0.4,
    })
    mock_agent.client.messages.create.return_value = MagicMock(
        content=[MagicMock(text=refined_response)]
    )
    original_prefs = {"favorite_genre": "folk", "favorite_mood": "sad",
                      "target_energy": 0.2, "target_valence": 0.2}
    result = mock_agent.refine("sad and empty", original_prefs, confidence=0.3)
    assert result["favorite_genre"] == "ambient"
    assert result["favorite_mood"] == "moody"


def test_refine_falls_back_on_bad_json(mock_agent):
    """refine() should return original prefs if Claude returns invalid JSON."""
    mock_agent.client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="oops not json")]
    )
    original_prefs = {"favorite_genre": "pop", "favorite_mood": "happy",
                      "target_energy": 0.8, "target_valence": 0.8}
    result = mock_agent.refine("test vibe", original_prefs, confidence=0.4)
    assert result == original_prefs
