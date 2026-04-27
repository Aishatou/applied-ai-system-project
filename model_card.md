# 🎧 Model Card: MoodMatcher Agent v2.0

> **Base project:** MoodMatcher 1.5 — CodePath AI110, Module 3
> The original system scored songs from an 18-song catalog against hardcoded user profiles using a weighted genre/mood/energy/valence formula. MoodMatcher Agent extends this into a self-evaluating, self-refining agentic loop.

---

## 1. Model Name

**MoodMatcher Agent v2.0**

---

## 2. Intended Use

MoodMatcher Agent accepts a free-text vibe description from a user and returns a ranked list of up to 5 song recommendations from an 18-song catalog, along with a confidence score for each run.

It is designed as a portfolio demonstration of agentic AI system design for CodePath AI110. It is not intended for production use or real users.

**Assumptions the system makes:**
- The user has a single vibe per session — no multi-session memory
- The catalog is fixed at 18 songs
- The system runs fully locally — no API key or internet connection required

---

## 3. How the Model Works

MoodMatcher Agent runs a 4-step loop every time a user describes their music vibe in plain English.

**Step 1 — Plan:** The user's free-text description (e.g., "sad late night energy") is passed through a keyword parser. The parser scans for known genre terms (like "lofi", "gothic", "techno"), mood terms (like "moody", "hype", "chill"), and energy/valence signal words (like "calm", "beast", "rainy"). It returns a structured preference dict with a genre, mood, target energy (0–1), and target valence (0–1). If nothing matches, it falls back to safe defaults.

**Step 2 — Act:** The original MoodMatcher 1.5 scoring engine (unchanged from Module 3) runs against all 18 songs using those parsed preferences. Each song is scored on genre match (+2.0), mood match (+1.0), energy similarity (up to +1.0), and valence similarity (up to +0.5). The top 5 are returned.

**Step 3 — Evaluate:** The agent computes a confidence score by averaging the top-5 scores and dividing by the maximum possible score (4.5). If confidence falls below 0.60, the result is flagged as low-quality.

**Step 4 — Refine:** When confidence is low, the agent automatically switches to a related genre using a predefined fallback map (e.g., lofi → ambient, edm → rock) and nudges the energy target toward the catalog midpoint. The recommender re-runs once and returns the updated results. If confidence was already sufficient, this step is skipped entirely.

Every step is written to `agent.log` so the full decision trail is always visible and auditable.

---

## 4. Data

Same 18-song catalog as Module 3, stored in `data/songs.csv`.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, edm, country, folk. Moods: happy, chill, intense, relaxed, focused, moody.

The dataset is small and Western-genre-skewed. It does not include R&B, classical, K-pop, reggae, or non-English language music. Songs were generated rather than sourced from real listener data, so the catalog does not reflect actual music popularity or cultural diversity. Several genres (country, folk, edm) have only one song each, which limits how well the system handles vibes that map to those genres.

---

## 5. Strengths

The agentic loop makes the system genuinely flexible — users describe a feeling instead of filling out a form. The keyword parser handled a wide range of natural language inputs during testing, including multi-word phrases and emotionally descriptive prompts. The evaluate-and-refine loop caught weak matches automatically and improved results without any user intervention. Full logging means every run is traceable. Because the system is fully local with no external API calls, it runs consistently, deterministically, and without cost.

---

## 6. Limitations and Bias

The genre dominance bias from Module 3 carries over: the +2.0 genre bonus still outweighs all other features combined in some cases. A user asking for high-energy ambient music will still get calm ambient songs at the top because genre match alone outweighs the energy mismatch.

Single-word vibe prompts with no context (like "gothic" or "techno") sometimes produce lower confidence results because the parser has less signal to work with. The catalog only has one EDM song, so even a perfectly parsed "gym hype" vibe produces low confidence because the other 4 top-5 slots are filled with non-EDM songs that drag the average score down.

The confidence threshold of 0.60 was chosen heuristically — there is no labeled evaluation dataset to validate it against. The refine step makes at most one retry, so a genuinely hard vibe can still produce a low-confidence final output.

---

## 7. Evaluation

**17 unit tests — all passing.** Tests cover all 4 agent steps and use mocked dependencies so they run without any API key or external service.

Three demo vibes were tested end-to-end:

| Vibe | Refined? | Final Confidence | Top Pick |
|------|----------|-----------------|----------|
| Sad late night energy | Yes (synthwave → ambient) | 0.58 | Rainy Window — Paper Lanterns |
| Gym hype bangers | Yes (edm → rock) | 0.52 | Storm Runner — Voltline |
| Chill Sunday lo-fi | No | 0.72 | Library Rain — Paper Lanterns |

The refine step was most effective when the initial genre parse landed on an underrepresented genre. It was least effective when the vibe fundamentally conflicted with catalog coverage — no amount of genre-switching fixes a catalog that only has one song in a category.

The most surprising finding: the gym hype vibe triggered refinement even though the intent was clearly parsed. The issue was catalog coverage, not parsing accuracy — confidence measures how well the top-5 matched overall, not just whether the #1 pick was correct.

---

## 8. Ethical Considerations

**Misuse prevention:** A vibe prompt could attempt keyword injection to force specific genre or mood outputs. Mitigation: all parsed values are validated against enum allowlists for genre and mood, and numeric values (energy, valence) are clamped to the 0.0–1.0 range. Out-of-range or unrecognized values are replaced with safe defaults.

**Transparency:** Every recommendation includes a plain-language explanation of exactly why each song scored the way it did. The confidence score is surfaced to the user so they know when results are uncertain.

**Data privacy:** The system does not store user vibe prompts beyond the current session log (`agent.log`), which is local only.

---

## 9. AI Collaboration

**Helpful suggestion:** Claude suggested using `pytest.fixture` combined with `MagicMock` to isolate API calls from test logic. This allowed the full test suite to run without any API credentials — a real improvement over testing with live API calls that would introduce cost, latency, and nondeterminism.

**Flawed suggestion:** Claude initially recommended using `ast.literal_eval()` instead of `json.loads()` to parse structured outputs from API responses. This approach fails silently on valid JSON floats in certain edge cases (e.g., values formatted as `0.80` in some environments). The bug was caught during testing and replaced with `json.loads()` wrapped in explicit `try/except` handling.

---

## 10. Future Work

- Replace the fixed confidence threshold (0.60) with one calibrated against a labeled evaluation dataset
- Expand the keyword maps using a real music taxonomy instead of manually curated lists
- Allow multiple refinement passes with a maximum retry limit (e.g., 3 attempts) instead of a single retry
- Add catalog diversity enforcement so the top-5 results never include more than 2 songs from the same artist
- Expand the catalog beyond 18 songs so niche vibe prompts have more options to match against
- Add session memory so returning users don't have to re-describe their vibe from scratch

---

## 11. Personal Reflection

Extending MoodMatcher into an agentic system made a previously invisible problem impossible to ignore. The genre bias was acceptable when profiles were hardcoded by a developer who understood the scoring math — but it becomes a real UX failure when a user types "high energy ambient" in plain English and gets calm songs back. The evaluate-and-refine loop forced me to confront that gap directly instead of ignoring it.

The most transferable lesson was treating the original recommender as a modular component rather than the whole product. That mental shift — from "the recommender is the system" to "the recommender is a tool inside a larger system" — changed how I approached the architecture entirely and is something I'll carry into every project going forward.

What surprised me most was how much a small catalog limits what an agentic loop can actually do. The agent can parse intent accurately and evaluate results honestly, but if the songs aren't there, no amount of refinement fixes it. That's a real constraint that platforms like Spotify solve with millions of data points — and it gave me a much clearer picture of what scale actually buys you in a recommendation system.