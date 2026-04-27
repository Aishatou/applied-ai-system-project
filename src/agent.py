"""
agent.py — MoodMatcher Agentic Workflow (No-API Version)

4-step agent loop:
  1. Plan     — parse a natural-language vibe into structured preferences (keyword matching)
  2. Act      — score all catalog songs using the original weighted scoring engine
  3. Evaluate — compute a confidence score to assess recommendation quality
  4. Refine   — if confidence is low, adjust preferences and re-run once
"""

import logging
from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs

# ---------------------------------------------------------------------------
# Logging — writes to agent.log so every run is traceable
# ---------------------------------------------------------------------------
logging.basicConfig(
    filename="agent.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_POSSIBLE_SCORE = 4.5   # genre(2.0) + mood(1.0) + energy(1.0) + valence(0.5)
CONFIDENCE_THRESHOLD = 0.60

# ---------------------------------------------------------------------------
# Keyword maps for vibe parsing
# ---------------------------------------------------------------------------

GENRE_KEYWORDS = {
    "lofi":       ["lofi", "lo-fi", "study", "coding", "chill beats", "bedroom"],
    "pop":        ["pop", "catchy", "radio", "mainstream", "sing along"],
    "rock":       ["rock", "guitar", "band", "grunge", "alt"],
    "ambient":    ["ambient", "atmospheric", "space", "dreamy", "meditation", "background"],
    "jazz":       ["jazz", "coffee shop", "cafe", "smooth", "mellow", "coffee"],
    "synthwave":  ["synthwave", "retro", "80s", "neon", "night drive", "late night", "drive"],
    "indie pop":  ["indie", "indie pop", "alternative pop", "feel good"],
    "hip hop":    ["hip hop", "hiphop", "rap", "beats", "flow"],
    "edm":        ["edm", "electronic", "dance", "club", "rave", "banger", "drop", "bass"],
    "country":    ["country", "southern", "acoustic guitar", "twang"],
    "folk":       ["folk", "acoustic", "campfire", "storytelling", "gentle"],
}

MOOD_KEYWORDS = {
    "happy":   ["happy", "joy", "upbeat", "cheerful", "positive", "good mood", "smile", "sunshine"],
    "chill":   ["chill", "relaxed", "calm", "easy", "laid back", "lazy", "sunday", "cozy", "soft"],
    "intense": ["intense", "hype", "gym", "workout", "pump", "energy", "fire", "aggressive", "beast", "banger"],
    "relaxed": ["relaxed", "slow", "peaceful", "gentle", "quiet", "wind down", "unwind"],
    "focused": ["focused", "focus", "concentrate", "work", "productivity", "study", "deep work"],
    "moody":   ["moody", "sad", "melancholy", "dark", "emotional", "zone out", "lonely", "empty",
                "night", "rainy", "nostalgic", "heartbreak", "cry", "feelings"],
}

HIGH_ENERGY_WORDS = ["hype", "gym", "workout", "pump", "intense", "banger", "club", "rave",
                     "fire", "beast", "fast", "loud", "maximum", "hard"]
LOW_ENERGY_WORDS  = ["chill", "calm", "slow", "soft", "quiet", "gentle", "sleep", "peaceful",
                     "relax", "unwind", "background", "dreamy", "lazy", "zone out"]

HIGH_VALENCE_WORDS = ["happy", "joy", "positive", "upbeat", "sunshine", "feel good", "smile"]
LOW_VALENCE_WORDS  = ["sad", "dark", "moody", "lonely", "heartbreak", "empty", "melancholy",
                      "cry", "feelings", "emotional", "night"]

DEFAULT_PREFS = {
    "favorite_genre": "pop",
    "favorite_mood":  "chill",
    "target_energy":  0.60,
    "target_valence": 0.60,
}

GENRE_FALLBACKS = {
    "lofi":      "ambient",
    "ambient":   "lofi",
    "edm":       "rock",
    "rock":      "edm",
    "pop":       "indie pop",
    "indie pop": "pop",
    "jazz":      "lofi",
    "synthwave": "ambient",
    "hip hop":   "pop",
    "country":   "folk",
    "folk":      "country",
}


class MusicAgent:
    """
    Agentic music recommender that extends MoodMatcher 1.5 with a
    self-evaluating, self-refining recommendation loop.
    No external API required — vibe parsing uses keyword matching.
    """

    def __init__(self, catalog_path: str = "data/songs.csv"):
        self.songs = load_songs(catalog_path)
        logger.info(f"MusicAgent initialized with {len(self.songs)} songs.")

    def plan(self, vibe_prompt: str) -> Dict:
        """Step 1: Parse free-text vibe into structured music preferences."""
        logger.info(f"[PLAN] Parsing vibe: '{vibe_prompt}'")
        tokens = vibe_prompt.lower()

        genre_scores = {genre: 0 for genre in GENRE_KEYWORDS}
        for genre, keywords in GENRE_KEYWORDS.items():
            for kw in keywords:
                if kw in tokens:
                    genre_scores[genre] += 1
        best_genre = max(genre_scores, key=genre_scores.get)
        if genre_scores[best_genre] == 0:
            best_genre = DEFAULT_PREFS["favorite_genre"]

        mood_scores = {mood: 0 for mood in MOOD_KEYWORDS}
        for mood, keywords in MOOD_KEYWORDS.items():
            for kw in keywords:
                if kw in tokens:
                    mood_scores[mood] += 1
        best_mood = max(mood_scores, key=mood_scores.get)
        if mood_scores[best_mood] == 0:
            best_mood = DEFAULT_PREFS["favorite_mood"]

        energy = 0.60
        for word in HIGH_ENERGY_WORDS:
            if word in tokens:
                energy = min(1.0, energy + 0.12)
        for word in LOW_ENERGY_WORDS:
            if word in tokens:
                energy = max(0.1, energy - 0.12)
        energy = round(energy, 2)

        valence = 0.60
        for word in HIGH_VALENCE_WORDS:
            if word in tokens:
                valence = min(1.0, valence + 0.12)
        for word in LOW_VALENCE_WORDS:
            if word in tokens:
                valence = max(0.1, valence - 0.12)
        valence = round(valence, 2)

        prefs = {
            "favorite_genre": best_genre,
            "favorite_mood":  best_mood,
            "target_energy":  energy,
            "target_valence": valence,
        }
        logger.info(f"[PLAN] Parsed preferences: {prefs}")
        return prefs

    def act(self, prefs: Dict, k: int = 5) -> List[Tuple]:
        """Step 2: Run the MoodMatcher scoring engine with the parsed preferences."""
        logger.info(f"[ACT] Running recommender | prefs={prefs}")
        results = recommend_songs(prefs, self.songs, k=k)
        if results:
            top = results[0]
            logger.info(f"[ACT] Top pick: '{top[0]['title']}' (score {top[1]:.2f})")
        return results

    def evaluate(self, recommendations: List[Tuple]) -> Tuple[float, bool]:
        """Step 3: Compute confidence = avg_score / MAX_POSSIBLE_SCORE."""
        if not recommendations:
            logger.warning("[EVALUATE] Empty list — confidence 0.0")
            return 0.0, False
        avg_score    = sum(score for _, score, _ in recommendations) / len(recommendations)
        confidence   = round(avg_score / MAX_POSSIBLE_SCORE, 3)
        is_confident = confidence >= CONFIDENCE_THRESHOLD
        logger.info(f"[EVALUATE] confidence={confidence:.3f} | is_confident={is_confident}")
        return confidence, is_confident

    def refine(self, prefs: Dict) -> Dict:
        """Step 4: Adjust preferences — switch genre and nudge energy toward catalog midpoint."""
        logger.info(f"[REFINE] Adjusting from: {prefs}")
        refined = prefs.copy()
        refined["favorite_genre"] = GENRE_FALLBACKS.get(prefs["favorite_genre"], "pop")
        energy = prefs["target_energy"]
        if energy > 0.85:
            refined["target_energy"] = round(energy - 0.15, 2)
        elif energy < 0.35:
            refined["target_energy"] = round(energy + 0.15, 2)
        logger.info(f"[REFINE] Refined to: {refined}")
        return refined

    def run(self, vibe_prompt: str) -> None:
        """Execute the full 4-step agentic loop and print formatted results."""
        print(f"\n{'='*58}")
        print(f"  Vibe : \"{vibe_prompt}\"")
        print(f"{'='*58}")

        print("\n  [1/4] PLAN   — Parsing your vibe into preferences...")
        prefs = self.plan(vibe_prompt)
        print(f"         Genre: {prefs['favorite_genre']}  |  Mood: {prefs['favorite_mood']}  |  Energy: {prefs['target_energy']}  |  Valence: {prefs['target_valence']}")

        print("\n  [2/4] ACT    — Scoring catalog and retrieving top picks...")
        results = self.act(prefs)

        print("\n  [3/4] EVAL   — Checking recommendation confidence...")
        confidence, is_confident = self.evaluate(results)
        status = "Good" if is_confident else "Low"
        print(f"         Confidence: {confidence:.2f}  ({status}, threshold: {CONFIDENCE_THRESHOLD})")

        refined = False
        if not is_confident:
            print("\n  [4/4] REFINE — Adjusting preferences and re-running...")
            refined_prefs = self.refine(prefs)
            print(f"         Genre: {prefs['favorite_genre']} -> {refined_prefs['favorite_genre']}  |  Energy: {prefs['target_energy']} -> {refined_prefs['target_energy']}")
            results       = self.act(refined_prefs)
            confidence, _ = self.evaluate(results)
            print(f"         Updated confidence: {confidence:.2f}")
            refined = True
        else:
            print("\n  [4/4] REFINE — Skipped (confidence is sufficient).")

        print(f"\n  {'─'*56}")
        print(f"  Top Recommendations {'(after refinement)' if refined else ''}")
        print(f"  {'─'*56}")
        for i, (song, score, reasons) in enumerate(results, 1):
            print(f"\n  #{i}  {song['title']} by {song['artist']}")
            print(f"       Score : {score:.2f}  |  Confidence: {confidence:.2f}")
            print(f"       Why   : {', '.join(reasons)}")

        print(f"\n{'='*58}\n")
        logger.info(f"[RUN] Done. vibe='{vibe_prompt}' | confidence={confidence:.3f} | refined={refined}")
