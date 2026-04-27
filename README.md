# 🎧 MoodMatcher Agent

> **Base Project:** MoodMatcher 1.5 — CodePath AI110, Module 3
> The original system scored songs from an 18-song catalog using hardcoded user profiles and a weighted genre/mood/energy/valence formula. MoodMatcher Agent extends this into a self-evaluating, self-refining agentic recommendation loop.

---

## 📺 Demo Walkthrough

🎬 **[Loom Video Walkthrough](https://www.loom.com/share/6fd9ed039cf647fdb4422a511b966851)** 

---

## 💡 What It Does

Instead of requiring hardcoded preferences, you describe your mood in plain English and the agent does the rest.

```
"sad late night energy, something slow and moody to zone out to"
      ↓
  Genre: ambient  |  Mood: moody  |  Energy: 0.36  |  Valence: 0.24
      ↓
  Top pick: Rainy Window by Paper Lanterns  (Score: 4.29)
```

The agent runs a **4-step loop** on every request:

| Step | What Happens |
|------|-------------|
| **1. Plan** | Keyword parser reads your vibe → extracts genre, mood, energy, valence |
| **2. Act** | Original MoodMatcher scoring engine scores all 18 songs → returns top 5 |
| **3. Evaluate** | Confidence score computed as `avg_score ÷ 4.5` — flagged if below 0.60 |
| **4. Refine** | If confidence is low, switches to a related genre, nudges energy, and re-runs once |

Every step is written to `agent.log` so the full decision trail is always visible.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│         User (plain-text vibe)          │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  STEP 1: PLAN                           │
│  Keyword parser → structured prefs      │
│  (genre, mood, target_energy, valence)  │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  STEP 2: ACT                            │
│  songs.csv → score_song()               │
│  → recommend_songs() → top-5 results    │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  STEP 3: EVALUATE                       │
│  confidence = avg_score / 4.5           │
│  threshold: 0.60                        │
└────────┬─────────────────┬──────────────┘
         │ ≥ 0.60          │ < 0.60
         ▼                 ▼
   ┌───────────┐   ┌──────────────────────┐
   │  RESULTS  │   │  STEP 4: REFINE      │
   └───────────┘   │  switch genre +      │
                   │  nudge energy →      │
                   │  re-run ACT + EVAL   │
                   └──────────┬───────────┘
                              ▼
                        ┌───────────┐
                        │  RESULTS  │
                        └───────────┘
                              │
                        agent.log (all steps logged)
```

**Key files:**

```
applied-ai-system-project/
├── src/
│   ├── agent.py            ← 4-step agentic loop (MusicAgent class)
│   └── recommender.py      ← original Module 3 scoring engine (unchanged)
├── data/
│   └── songs.csv           ← 18-song catalog
├── tests/
│   ├── test_agent.py       ← 15 agent unit tests
│   └── test_recommender.py ← original 2 Module 3 tests
├── assets/                 ← diagrams and screenshots
├── agent_main.py           ← entry point (demo + interactive mode)
├── main.py                 ← original Module 3 runner
├── conftest.py             ← pytest path config
├── agent.log               ← auto-generated run log
└── requirements.txt
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/Aishatou/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Install dependencies
```bash
pip install pytest
```
No API key needed. The system runs fully locally.

### 3. Run the agent
```bash
python agent_main.py
```
- Choose **1** for demo mode (3 preset vibes run automatically)
- Choose **2** for interactive mode (type your own vibe)

### 4. Run the original recommender
```bash
python main.py
```

### 5. Run all tests
```bash
pytest tests/ -v
```

---

## 💬 Sample Interactions

### Input 1 — Sad Late Night
```
Vibe: "sad late night energy, something slow and moody to zone out to"

[1/4] PLAN   → Genre: synthwave  |  Mood: moody  |  Energy: 0.36  |  Valence: 0.24
[2/4] ACT    → Scored 18 songs
[3/4] EVAL   → Confidence: 0.57 — Low, triggering refinement
[4/4] REFINE → Genre: synthwave → ambient  |  Updated confidence: 0.58

#1  Rainy Window by Paper Lanterns       Score: 4.29
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.86), valence similarity (+0.43)
#2  Spacewalk Thoughts by Orbit Bloom    Score: 3.21
#3  Velvet Underground by Slow Stereo    Score: 2.33
```

### Input 2 — Gym Hype
```
Vibe: "I need maximum hype for the gym, nothing but high energy bangers"

[1/4] PLAN   → Genre: edm  |  Mood: intense  |  Energy: 1.0  |  Valence: 0.6
[2/4] ACT    → Scored 18 songs
[3/4] EVAL   → Confidence: 0.51 — Low, triggering refinement
[4/4] REFINE → Genre: edm → rock  |  Energy: 1.0 → 0.85  |  Updated confidence: 0.52

#1  Storm Runner by Voltline       Score: 4.38
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.94), valence similarity (+0.44)
#2  Bass Drop Arena by Voltline    Score: 2.36
#3  Gym Hero by Max Pulse          Score: 2.33
```

### Input 3 — Chill Sunday
```
Vibe: "chill Sunday morning, coffee in hand, lo-fi and relaxed vibes"

[1/4] PLAN   → Genre: lofi  |  Mood: chill  |  Energy: 0.36  |  Valence: 0.6
[2/4] ACT    → Scored 18 songs
[3/4] EVAL   → Confidence: 0.72 — Good, no refinement needed
[4/4] REFINE → Skipped

#1  Library Rain by Paper Lanterns     Score: 4.49
    Why: genre match (+2.0), mood match (+1.0), energy similarity (+0.99), valence similarity (+0.50)
#2  Midnight Coding by LoRoom          Score: 4.42
#3  Focus Flow by LoRoom               Score: 3.46
```

---

## 🧠 Design Decisions

**Why keyword parsing instead of an LLM API?**
No API key, no cost, no rate limits, fully deterministic — every run produces the same output for the same input, which makes it testable and reproducible.

**Why keep the original `recommender.py` unchanged?**
The agent wraps the original scoring engine as a modular component rather than replacing it. This demonstrates agentic design — the recommender is a tool the agent calls, not the whole system.

**Why confidence = avg_score ÷ 4.5?**
The max possible score is 4.5 (genre +2.0, mood +1.0, energy +1.0, valence +0.5). Dividing by 4.5 gives a normalized 0–1 range that's directly interpretable and derived from the existing system — no extra ML needed.

**Why only one refinement pass?**
A single retry keeps the loop bounded. If the catalog genuinely doesn't cover a vibe, infinite retries won't fix it — being transparent about low confidence is more honest than masking it.

**Why mock the API in tests?**
Tests never hit external services, so they run offline, instantly, and in any environment.

---

## 🧪 Testing Summary

```bash
pytest tests/ -v
# 17 passed in 0.10s
```

| Group | Tests | Status |
|-------|-------|--------|
| PLAN — keyword parsing | 5 | ✅ All pass |
| ACT — scoring & ranking | 3 | ✅ All pass |
| EVALUATE — confidence logic | 4 | ✅ All pass |
| REFINE — genre switch & energy nudge | 3 | ✅ All pass |
| Original Module 3 tests | 2 | ✅ All pass |

**What worked:** Confidence scoring correctly flagged weak matches. The refine step reliably switched to related genres and re-ran. All edge cases handled without crashing.

**What struggled:** Single-word vibe prompts with no context sometimes hit catalog gaps and returned lower confidence results. This is a catalog size limitation, not a logic bug.

**Surprising finding:** The gym hype vibe triggered refinement even though the intent was clear — because the catalog only has one EDM song, the average score across top-5 was dragged down by non-EDM filler. Confidence measures catalog coverage, not just intent accuracy.

---

## 💭 Reflection & Ethics

**Limitations**
The genre bias from Module 3 (+2.0 bonus) carries over. The 18-song catalog means niche vibes will always produce weak results regardless of parsing quality. The confidence threshold (0.60) was chosen heuristically with no labeled dataset to validate it against.

**Potential misuse**
Vibe prompts could attempt keyword injection to manipulate genre or mood selection. Mitigation: all outputs are validated against enum allowlists and numeric values are clamped to valid ranges.

**AI Collaboration**
- ✅ Helpful: Claude suggested the `pytest.fixture` + `MagicMock` pattern, which kept all tests runnable without any API key.
- ❌ Flawed: Claude initially suggested `ast.literal_eval()` to parse structured outputs — this fails silently on certain float formats. Replaced with `json.loads()` + explicit error handling after catching the issue in testing.

---

## 🔮 Future Work

- Replace fixed confidence threshold with one calibrated against labeled evaluation data
- Expand keyword maps using a real music taxonomy
- Add catalog diversity enforcement so top-5 never includes more than 2 songs from the same artist
- Expand catalog beyond 18 songs for better niche vibe coverage
- Add session memory so returning users don't re-describe their vibe each time




