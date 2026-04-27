"""
agent.py — MoodMatcher Agentic Workflow

4-step agent loop:
  1. Plan     — parse a natural-language vibe into structured preferences (Claude API)
  2. Act      — score all catalog songs and retrieve top-k
  3. Evaluate — compute a confidence score for the picks
  4. Refine   — if confidence is low, ask Claude to adjust preferences and re-run once
"""

import json
import logging
import anthropic
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

VALID_GENRES = ["pop", "lofi", "rock", "ambient", "jazz",
                "synthwave", "indie pop", "hip hop", "edm", "country", "folk"]
VALID_MOODS  = ["happy", "chill", "intense", "relaxed", "focused", "moody"]


class MusicAgent:
    """
    Agentic music recommender that extends MoodMatcher 1.5 with a
    self-evaluating, self-refining recommendation loop powered by Claude.
    """

    def __init__(self, catalog_path: str = "data/songs.csv"):
        self.songs = load_songs(catalog_path)
        self.client = anthropic.Anthropic()
        logger.info(f"MusicAgent initialized with {len(self.songs)} songs.")

    # -----------------------------------------------------------------------
    # STEP 1: PLAN
    # -----------------------------------------------------------------------
    def plan(self, vibe_prompt: str) -> Dict:
        """
        Send the user's free-text vibe to Claude and parse the response
        into structured preferences the recommender can use.

        Returns:
            dict with keys: favorite_genre, favorite_mood,
                            target_energy, target_valence
        """
        logger.info(f"[PLAN] Parsing vibe: '{vibe_prompt}'")

        system = (
            "You are a music preference parser. "
            "Given a user's vibe description, return ONLY a valid JSON object with these keys:\n"
            f"  favorite_genre  — one of {VALID_GENRES}\n"
            f"  favorite_mood   — one of {VALID_MOODS}\n"
            "  target_energy   — float 0.0–1.0 (how energetic the music should be)\n"
            "  target_valence  — float 0.0–1.0 (how positive/upbeat the music should be)\n"
            "Return ONLY the JSON object. No explanation, no markdown, no backticks."
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": vibe_prompt}],
            )
            raw = response.content[0].text.strip()
            logger.info(f"[PLAN] Claude returned: {raw}")
            prefs = json.loads(raw)

            # Validate and clamp values
            if prefs.get("favorite_genre") not in VALID_GENRES:
                prefs["favorite_genre"] = "pop"
            if prefs.get("favorite_mood") not in VALID_MOODS:
                prefs["favorite_mood"] = "chill"
            prefs["target_energy"]  = max(0.0, min(1.0, float(prefs.get("target_energy", 0.6))))
            prefs["target_valence"] = max(0.0, min(1.0, float(prefs.get("target_valence", 0.5))))

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"[PLAN] Parsing failed ({e}); using safe fallback preferences.")
            prefs = {
                "favorite_genre": "pop",
                "favorite_mood": "chill",
                "target_energy": 0.6,
                "target_valence": 0.6,
            }

        logger.info(f"[PLAN] Final preferences: {prefs}")
        return prefs

    # -----------------------------------------------------------------------
    # STEP 2: ACT
    # -----------------------------------------------------------------------
    def act(self, prefs: Dict, k: int = 5) -> List[Tuple]:
        """
        Run the existing MoodMatcher scoring engine with the parsed preferences.

        Returns:
            List of (song_dict, score, reasons) tuples, sorted descending by score.
        """
        logger.info(f"[ACT] Running recommender | prefs={prefs}")
        results = recommend_songs(prefs, self.songs, k=k)
        if results:
            top = results[0]
            logger.info(f"[ACT] Top pick: '{top[0]['title']}' by {top[0]['artist']} "
                        f"(score {top[1]:.2f})")
        return results

    # -----------------------------------------------------------------------
    # STEP 3: EVALUATE
    # -----------------------------------------------------------------------
    def evaluate(self, recommendations: List[Tuple]) -> Tuple[float, bool]:
        """
        Compute a confidence score as the average normalized score
        across the top-k recommendations.

        Confidence = avg_score / MAX_POSSIBLE_SCORE

        Returns:
            (confidence: float, is_confident: bool)
        """
        if not recommendations:
            logger.warning("[EVALUATE] Empty recommendation list — confidence 0.0")
            return 0.0, False

        avg_score = sum(score for _, score, _ in recommendations) / len(recommendations)
        confidence = round(avg_score / MAX_POSSIBLE_SCORE, 3)
        is_confident = confidence >= CONFIDENCE_THRESHOLD

        logger.info(
            f"[EVALUATE] avg_score={avg_score:.2f} | "
            f"confidence={confidence:.3f} | "
            f"is_confident={is_confident}"
        )
        return confidence, is_confident

    # -----------------------------------------------------------------------
    # STEP 4: REFINE
    # -----------------------------------------------------------------------
    def refine(self, vibe_prompt: str, prefs: Dict, confidence: float) -> Dict:
        """
        When confidence is below threshold, ask Claude to suggest adjusted
        preferences that better fit the catalog, then return the new prefs.

        Returns:
            Refined preference dict (same structure as plan() output).
        """
        logger.info(
            f"[REFINE] Confidence {confidence:.3f} < {CONFIDENCE_THRESHOLD} — "
            "requesting Claude refinement."
        )

        system = (
            "You are a music preference optimizer. "
            "The current preferences produced low-confidence recommendations. "
            "Given the original vibe and current preferences, suggest adjusted preferences "
            "that are more likely to find strong catalog matches. "
            f"Available genres: {VALID_GENRES}\n"
            f"Available moods:  {VALID_MOODS}\n"
            "Return ONLY a JSON object with keys: "
            "favorite_genre, favorite_mood, target_energy, target_valence. "
            "No explanation, no markdown, no backticks."
        )

        user_content = (
            f"Original vibe: '{vibe_prompt}'\n"
            f"Current preferences: {json.dumps(prefs)}\n"
            f"Confidence score: {confidence:.3f} (threshold: {CONFIDENCE_THRESHOLD})\n"
            "Suggest better-fitting preferences."
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                system=system,
                messages=[{"role": "user", "content": user_content}],
            )
            raw = response.content[0].text.strip()
            logger.info(f"[REFINE] Claude suggested: {raw}")
            refined = json.loads(raw)

            if refined.get("favorite_genre") not in VALID_GENRES:
                refined["favorite_genre"] = prefs["favorite_genre"]
            if refined.get("favorite_mood") not in VALID_MOODS:
                refined["favorite_mood"] = prefs["favorite_mood"]
            refined["target_energy"]  = max(0.0, min(1.0, float(refined.get("target_energy", prefs["target_energy"]))))
            refined["target_valence"] = max(0.0, min(1.0, float(refined.get("target_valence", prefs["target_valence"]))))

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"[REFINE] Parsing failed ({e}); keeping original preferences.")
            refined = prefs

        logger.info(f"[REFINE] Refined preferences: {refined}")
        return refined

    # -----------------------------------------------------------------------
    # FULL AGENT LOOP
    # -----------------------------------------------------------------------
    def run(self, vibe_prompt: str) -> None:
        """
        Execute the complete 4-step agentic loop and print formatted results.

        Args:
            vibe_prompt: A free-text description of the user's music vibe.
        """
        print(f"\n{'='*58}")
        print(f"  🎧  MoodMatcher Agent — Agentic Music Recommender")
        print(f"  Vibe : \"{vibe_prompt}\"")
        print(f"{'='*58}")

        # ── Step 1: Plan ──────────────────────────────────────────────────
        print("\n  [1/4] PLAN  — Parsing your vibe into preferences...")
        prefs = self.plan(vibe_prompt)
        print(f"         Genre: {prefs['favorite_genre']}  |  "
              f"Mood: {prefs['favorite_mood']}  |  "
              f"Energy: {prefs['target_energy']}  |  "
              f"Valence: {prefs['target_valence']}")

        # ── Step 2: Act ───────────────────────────────────────────────────
        print("\n  [2/4] ACT   — Scoring catalog and retrieving top picks...")
        results = self.act(prefs)

        # ── Step 3: Evaluate ──────────────────────────────────────────────
        print("\n  [3/4] EVAL  — Checking recommendation confidence...")
        confidence, is_confident = self.evaluate(results)
        status = "✅ Good" if is_confident else "⚠️  Low"
        print(f"         Confidence: {confidence:.2f}  ({status}, threshold: {CONFIDENCE_THRESHOLD})")

        # ── Step 4: Refine (only if needed) ──────────────────────────────
        refined = False
        if not is_confident:
            print("\n  [4/4] REFINE — Adjusting preferences and re-running...")
            refined_prefs = self.refine(vibe_prompt, prefs, confidence)
            print(f"         New genre: {refined_prefs['favorite_genre']}  |  "
                  f"Mood: {refined_prefs['favorite_mood']}  |  "
                  f"Energy: {refined_prefs['target_energy']}")
            results   = self.act(refined_prefs)
            confidence, _ = self.evaluate(results)
            print(f"         Updated confidence: {confidence:.2f}")
            prefs   = refined_prefs
            refined = True
        else:
            print("\n  [4/4] REFINE — Skipped (confidence is sufficient).")

        # ── Results ───────────────────────────────────────────────────────
        print(f"\n  {'─'*56}")
        print(f"  🎵  Top Recommendations {'(after refinement)' if refined else ''}")
        print(f"  {'─'*56}")
        for i, (song, score, reasons) in enumerate(results, 1):
            print(f"\n  #{i}  {song['title']} by {song['artist']}")
            print(f"       Score      : {score:.2f}  |  Confidence: {confidence:.2f}")
            print(f"       Why        : {', '.join(reasons)}")

        print(f"\n{'='*58}\n")
        logger.info(f"[RUN] Done. vibe='{vibe_prompt}' | final_confidence={confidence:.3f} | refined={refined}")
