# 🎧 MoodMatcher Agent — Applied AI Music Recommendation System

> **Base Project:** MoodMatcher 1.5 (CodePath AI110 Module 3)
> The original system was a content-based music recommender that scored songs from an 18-song catalog against a user's hardcoded genre, mood, energy, and valence preferences using a weighted scoring formula.

---

## 📺 Demo Walkthrough

> 🎬 **[Loom Video Walkthrough](https://www.loom.com/share/YOUR_LINK_HERE)** ← replace with your Loom link before submitting

---

## 📋 Summary

**MoodMatcher Agent** extends the original recommender into a full agentic AI system. Instead of requiring hardcoded user profiles, users now describe their mood in plain English (e.g., *"sad late night energy"*), and the agent automatically:

1. **Plans** — parses the vibe into structured music preferences using Claude
2. **Acts** — scores all catalog songs using the original weighted scoring engine
3. **Evaluates** — computes a confidence score to assess recommendation quality
4. **Refines** — if confidence is below 0.60, asks Claude to adjust preferences and re-runs automatically

This turns a static script into a self-correcting, AI-powered recommendation loop.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User (plain text vibe)                │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│  STEP 1: PLAN                                          │
│  Claude API → parse vibe → structured prefs dict       │
│  (genre, mood, target_energy, target_valence)          │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│  STEP 2: ACT                                           │
│  MoodMatcher Scoring Engine (original recommender)     │
│  songs.csv → score_song() → recommend_songs() → top-5  │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│  STEP 3: EVALUATE                                      │
│  Confidence = avg_score / 4.5 (max possible)           │
│  Threshold: 0.60                                       │
└─────────────┬──────────────────────┬───────────────────┘
              │ confidence ≥ 0.60    │ confidence < 0.60
              ▼                      ▼
       ┌──────────────┐   ┌──────────────────────────┐
       │  FINAL       │   │  STEP 4: REFINE           │
       │  RESULTS     │   │  Claude API → adjust prefs │
       └──────────────┘   │  → re-run ACT + EVALUATE  │
                          └──────────┬────────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │  FINAL       │
                              │  RESULTS     │
                              └──────────────┘
                                     │
                              agent.log (all steps)
```

**Key Components:**
- `src/agent.py` — the 4-step agentic loop (`MusicAgent` class)
- `src/recommender.py` — original scoring engine (unchanged from Module 3)
- `agent_main.py` — entry point with demo + interactive modes
- `data/songs.csv` — 18-song catalog
- `agent.log` — auto-generated run log for traceability
- `tests/test_agent.py` — unit tests for all agent steps

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Install dependencies
```bash
pip install anthropic pytest
```

### 3. Set your Anthropic API key
```bash
# macOS / Linux
export ANTHROPIC_API_KEY="your-key-here"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=your-key-here
```
You can get a free API key at [console.anthropic.com](https://console.anthropic.com).

### 4. Run the agent
```bash
python agent_main.py
```
Choose **1** for the demo (3 preset vibes) or **2** for interactive mode.

### 5. Run the original recommender (unchanged)
```bash
python main.py
```

### 6. Run all tests
```bash
pytest tests/ -v
```

---

## 💬 Sample Interactions

### Input 1: Sad Late Night
```
Vibe: "sad late night energy, something slow and moody to zone out to"

[1/4] PLAN  → Genre: ambient | Mood: moody | Energy: 0.25 | Valence: 0.35
[2/4] ACT   → Scored 18 songs
[3/4] EVAL  → Confidence: 0.51 ⚠️ Low
[4/4] REFINE → Adjusted: Genre: synthwave | Mood: moody | Energy: 0.30
              Updated confidence: 0.64 ✅

#1  Rainy Window by Paper Lanterns       Score: 2.88
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.97) ...
#2  Night Drive Loop by Neon Echo        Score: 2.44
#3  Spacewalk Thoughts by Orbit Bloom    Score: 2.11
```

### Input 2: Gym Hype
```
Vibe: "I need maximum hype for the gym, nothing but high energy bangers"

[1/4] PLAN  → Genre: edm | Mood: intense | Energy: 0.95 | Valence: 0.65
[2/4] ACT   → Scored 18 songs
[3/4] EVAL  → Confidence: 0.74 ✅ Good
[4/4] REFINE → Skipped (confidence sufficient)

#1  Bass Drop Arena by Voltline    Score: 4.48
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.99) ...
#2  Storm Runner by Voltline       Score: 2.44
#3  Gym Hero by Max Pulse          Score: 2.41
```

### Input 3: Chill Sunday Morning
```
Vibe: "chill Sunday morning, coffee in hand, lo-fi and relaxed vibes"

[1/4] PLAN  → Genre: lofi | Mood: chill | Energy: 0.40 | Valence: 0.60
[2/4] ACT   → Scored 18 songs
[3/4] EVAL  → Confidence: 0.82 ✅ Good
[4/4] REFINE → Skipped (confidence sufficient)

#1  Midnight Coding by LoRoom        Score: 4.47
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.98) ...
#2  Library Rain by Paper Lanterns   Score: 4.44
#3  Focus Flow by LoRoom             Score: 3.50
```

---

## 🧠 Design Decisions

| Decision | Rationale | Trade-off |
|---|---|---|
| Claude for vibe parsing | Natural language → structured prefs without manual mapping | Requires API key; adds latency |
| Keep original scoring engine unchanged | Preserves Module 3 work; agent wraps it rather than replacing it | Genre bias from original still present |
| Confidence = avg_score / 4.5 | Simple, transparent, derived from existing score range | Doesn't account for catalog diversity |
| Single refinement pass | Keeps loop bounded; avoids infinite retry | One pass may not fully resolve low confidence |
| Mock Anthropic in tests | Tests run locally without API key or cost | Agent behavior with real API not tested by unit tests |

---

## 🧪 Testing Summary

**Test suite:** `tests/test_agent.py` + `tests/test_recommender.py`

| Test | Status | Notes |
|---|---|---|
| `test_act_returns_top_k_results` | ✅ Pass | Correct k-limit behavior |
| `test_act_sorts_by_score_descending` | ✅ Pass | Ranking is always descending |
| `test_act_top_song_matches_genre` | ✅ Pass | Genre match rises to #1 |
| `test_evaluate_perfect_score_gives_confidence_one` | ✅ Pass | Max score → confidence 1.0 |
| `test_evaluate_low_score_fails_threshold` | ✅ Pass | Low score → is_confident False |
| `test_evaluate_empty_list_returns_zero` | ✅ Pass | No crash on empty input |
| `test_evaluate_confidence_is_normalized` | ✅ Pass | Always 0.0–1.0 |
| `test_plan_parses_valid_json` | ✅ Pass | Correct parsing from mocked API |
| `test_plan_falls_back_on_bad_json` | ✅ Pass | Graceful fallback on bad response |
| `test_refine_returns_adjusted_prefs` | ✅ Pass | Returns Claude's suggested prefs |
| `test_refine_falls_back_on_bad_json` | ✅ Pass | Returns original prefs on failure |

**11 / 11 tests passing.**

The system struggled most with underrepresented moods — the vibe *"sad"* has no direct catalog match, which triggers refinement most consistently. Confidence averaged ~0.71 across the 3 demo vibes; the gym prompt scored highest (0.74) because the edm/intense catalog entry is a strong match.

---

## 💭 Reflection and Ethics

### Limitations
- **Genre dominance bias** — the original +2.0 genre bonus carries over; a perfect mood+energy match without genre still loses.
- **Small catalog** — 18 songs means some vibe prompts will always produce weak matches regardless of how well prefs are parsed.
- **Claude dependency** — if the API is unavailable, plan() and refine() fall back to generic defaults silently.

### Potential Misuse
The system could theoretically be prompted to manipulate recommendations (e.g., "always recommend EDM regardless of vibe") via prompt injection in the vibe field. Mitigation: the system validates all Claude outputs against allowed genre/mood enums and clamps numeric values.

### Surprises During Testing
Claude was remarkably consistent at parsing ambiguous vibes — *"I want to disappear into music"* reliably mapped to `ambient/moody/low energy`. The refinement step surprised me by sometimes making genre shifts rather than energy adjustments, which was unexpected but often effective.

### AI Collaboration
- **Helpful:** Claude suggested using `pytest.fixture` with `MagicMock` for the test suite, which cleanly isolated all API calls from test logic.
- **Flawed:** Claude initially suggested using `ast.literal_eval` instead of `json.loads` for parsing API responses — this would have crashed on floats formatted like `0.80` in some edge cases. Caught during testing.

---

## 📁 Project Structure

```
applied-ai-system-project/
├── src/
│   ├── agent.py            ← NEW: 4-step agentic loop
│   └── recommender.py      ← original Module 3 scoring engine
├── data/
│   └── songs.csv           ← 18-song catalog
├── tests/
│   ├── test_agent.py       ← NEW: agent unit tests (11 tests)
│   └── test_recommender.py ← original Module 3 tests
├── assets/
│   └── architecture.png    ← system diagram (export from README)
├── agent_main.py           ← NEW: agentic entry point
├── main.py                 ← original Module 3 runner
├── README.md               ← this file
├── model_card.md           ← updated reflection card
├── agent.log               ← auto-generated run log
└── requirements.txt        ← anthropic, pytest
```
