# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:
The system compares each song in the catalog against the user's taste profile using a weighted scoring rule. Genre and mood are rewarded with fixed bonus points for exact matched, while numerical features like energy with valence are scored by proximity - the closer a song's value is to the user's target, the higher it scores. All songs are then ranked and the top K results are returned. 

- What features does each `Song` use in your system
  - genre : categorical exact match scoring 
  - mood : categorical, exact match scoring 
  - energy : numerical (0.0-1.0), proximity scoring 
  - valence : numerical (0.0-1.0), proximity scoring
- What information does your `UserProfile` store
    - 'favorit_genre': preferred genre string 
    - 'favorite_mood': preferred mood string 
    - 'target_energy' : ideal energy level (0.0-1.0)
    - 'target_valence' : ideal valence level (0.0-1.0)
- How does your `Recommender` compute a score for each song
  - Genre Match : +2.0 points 
  - Mood Match : +1.0 points 
  - Energy Similarity : up to +1.0 points '((1.0 - abs)song_energy - target_energy)'
  - Valence Similarity : up to +0.5 points'(1.0-abs(song_valence - target_valence))
- How do you choose which songs to recommend

You can include a simple diagram or bullet list if helpful.
'''mermaid
flowchart TD
    A[User Profile\ngenre, mood, energy, valence] --> B[Load songs.csv]
    B --> C[For each song in catalog]
    C --> D{Genre match?}
    D --> |Yes| E[+2.0 points]
    D --> |No| F[+0 points]
    E --> G{Mood match?}
    F --> G
    G --> |Yes| H[+1.0 points]
    G --> |No| I[+0 points]
    H --> J[Energy Similarity Score\n1.0- abs difference x 1.0]
    I --> J 
    J --> K[Valence Similarity Score\n1.0 - abs difference x 0.5]
    K --> L[Total Score for Song]
    L --> M{More Songs? }
    M --> |Yes| C
    M --> |No| N[Sort All Songs by Score\nhighest to lowest]
    M --> O[Return Top K Recommendations]
'''

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation
Building this recommender made clear how much a single design decision — like the genre weight — can shape every result the system produces. A score that feels mathematically reasonable can still produce recommendations that miss what the user actually wants, as the Conflicted Listener experiment showed. Real platforms like Spotify face the same tradeoffs but have millions of behavioral signals to balance them out. This project changed how I think about recommendation systems: what feels like a smart suggestion is often just math that someone chose, and those choices carry real consequences for what users do and do not get shown.
## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0
MusicMatcher 1.5


---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"


## Screenshots 

Original Weight Output : 
![Original Weights Output](Original%20Weight.png)

Experiment Results Output : 
![Experiment Results Output](Result.png)

