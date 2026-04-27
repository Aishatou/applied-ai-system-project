"""
test_agent.py — Unit tests for the MoodMatcher agentic loop.

No API key required. Run with:
    pytest tests/test_agent.py -v
"""

import pytest
from src.agent import MusicAgent, MAX_POSSIBLE_SCORE, CONFIDENCE_THRESHOLD

SAMPLE_SONGS = [
    {"id": 1,  "title": "Sunrise City",      "artist": "Neon Echo",      "genre": "pop",      "mood": "happy",   "energy": 0.82, "tempo_bpm": 118.0, "valence": 0.84, "danceability": 0.79, "acousticness": 0.18},
    {"id": 2,  "title": "Midnight Coding",   "artist": "LoRoom",         "genre": "lofi",     "mood": "chill",   "energy": 0.42, "tempo_bpm": 78.0,  "valence": 0.56, "danceability": 0.62, "acousticness": 0.71},
    {"id": 12, "title": "Bass Drop Arena",   "artist": "Voltline",       "genre": "edm",      "mood": "intense", "energy": 0.95, "tempo_bpm": 140.0, "valence": 0.52, "danceability": 0.91, "acousticness": 0.03},
    {"id": 3,  "title": "Storm Runner",      "artist": "Voltline",       "genre": "rock",     "mood": "intense", "energy": 0.91, "tempo_bpm": 152.0, "valence": 0.48, "danceability": 0.66, "acousticness": 0.10},
    {"id": 6,  "title": "Spacewalk Thoughts","artist": "Orbit Bloom",    "genre": "ambient",  "mood": "chill",   "energy": 0.28, "tempo_bpm": 60.0,  "valence": 0.65, "danceability": 0.41, "acousticness": 0.92},
]

@pytest.fixture
def agent():
    a = MusicAgent.__new__(MusicAgent)
    a.songs = SAMPLE_SONGS
    return a


# ── PLAN tests ────────────────────────────────────────────────────────────

def test_plan_gym_maps_to_intense(agent):
    """'gym workout' should map to intense mood and high energy."""
    prefs = agent.plan("gym workout hype banger")
    assert prefs["favorite_mood"] == "intense"
    assert prefs["target_energy"] > 0.7

def test_plan_lofi_study_maps_correctly(agent):
    """'lofi study' should map to lofi genre."""
    prefs = agent.plan("lofi study beats for coding")
    assert prefs["favorite_genre"] == "lofi"

def test_plan_sad_maps_to_moody(agent):
    """Sad/emotional keywords should produce moody mood."""
    prefs = agent.plan("sad melancholy late night feelings")
    assert prefs["favorite_mood"] == "moody"

def test_plan_returns_all_keys(agent):
    """plan() should always return all 4 required keys."""
    prefs = agent.plan("something random and weird")
    assert "favorite_genre"  in prefs
    assert "favorite_mood"   in prefs
    assert "target_energy"   in prefs
    assert "target_valence"  in prefs

def test_plan_energy_clamped(agent):
    """Energy should always be between 0.1 and 1.0."""
    prefs = agent.plan("hype gym workout pump fire beast fast loud maximum hard banger")
    assert 0.0 <= prefs["target_energy"] <= 1.0


# ── ACT tests ─────────────────────────────────────────────────────────────

def test_act_returns_top_k(agent):
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy",
             "target_energy": 0.8, "target_valence": 0.8}
    results = agent.act(prefs, k=2)
    assert len(results) <= 2

def test_act_sorts_descending(agent):
    prefs = {"favorite_genre": "edm", "favorite_mood": "intense",
             "target_energy": 0.95, "target_valence": 0.5}
    results = agent.act(prefs, k=5)
    scores = [s for _, s, _ in results]
    assert scores == sorted(scores, reverse=True)

def test_act_top_song_matches_genre(agent):
    prefs = {"favorite_genre": "edm", "favorite_mood": "intense",
             "target_energy": 0.95, "target_valence": 0.5}
    results = agent.act(prefs, k=5)
    assert results[0][0]["genre"] == "edm"


# ── EVALUATE tests ────────────────────────────────────────────────────────

def test_evaluate_max_score_gives_confidence_one(agent):
    recs = [(SAMPLE_SONGS[0], MAX_POSSIBLE_SCORE, ["genre match"])]
    confidence, is_confident = agent.evaluate(recs)
    assert confidence == 1.0
    assert is_confident is True

def test_evaluate_low_score_fails_threshold(agent):
    recs = [(SAMPLE_SONGS[1], 0.9, ["energy similarity (+0.50)"])]
    confidence, is_confident = agent.evaluate(recs)
    assert confidence < CONFIDENCE_THRESHOLD
    assert is_confident is False

def test_evaluate_empty_returns_zero(agent):
    confidence, is_confident = agent.evaluate([])
    assert confidence == 0.0
    assert is_confident is False

def test_evaluate_confidence_in_range(agent):
    recs = [(SAMPLE_SONGS[2], 3.5, ["genre match"])]
    confidence, _ = agent.evaluate(recs)
    assert 0.0 <= confidence <= 1.0


# ── REFINE tests ──────────────────────────────────────────────────────────

def test_refine_switches_genre(agent):
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill",
             "target_energy": 0.4, "target_valence": 0.6}
    refined = agent.refine(prefs)
    assert refined["favorite_genre"] != prefs["favorite_genre"]

def test_refine_nudges_high_energy_down(agent):
    prefs = {"favorite_genre": "edm", "favorite_mood": "intense",
             "target_energy": 0.95, "target_valence": 0.5}
    refined = agent.refine(prefs)
    assert refined["target_energy"] < prefs["target_energy"]

def test_refine_nudges_low_energy_up(agent):
    prefs = {"favorite_genre": "ambient", "favorite_mood": "chill",
             "target_energy": 0.20, "target_valence": 0.4}
    refined = agent.refine(prefs)
    assert refined["target_energy"] > prefs["target_energy"]
