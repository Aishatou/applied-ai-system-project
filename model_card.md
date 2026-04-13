# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Suggests the top 5 songs from an 18-song catalog based on a user's preferred genre, mood, energy level, and valence. It is designed for classroom exploration of how content-based recommendation systems work. Its is not intended for real users or production use. The system assumes the user has a single, consistent taste profile and does not account for changing moods or listening context. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

Suggests the top 5 songs from an 18-song catalog based on a user's preferred genre, mood, energy level, and valence. It is designed for classroom exploration of how content-based recommendation systems work. Its is not intended for real users or production use. The system assumes the user has a single, consistent taste profile and does not account for changing moods or listening context.
 

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The recommender looks at each song in the catalog and gives it a score based on how well it matched what the user likes. It checks thwo things exactly : Does the song's genre mathc the user's favorite genere? and Does the mood match ? . If the genres matches, the song gets a big bonus. If the mood matches, it gets a smaller bonus, then it looks at the energy determining how intense or calm the song is, and gives more point the closer it is to what the user wants. It does the same for valence, which is basically how positive or upbeat a song sounds. Every song gets a final total score and the top 5 are returned, highest to lowest.

---

## 4. Data  

Describe the dataset the model uses.  
The catalog contains 18 songs stored in a CSV file. Genres represented include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, edm , country, and folk. Moods include happy, chill, intense, relaxed, focused, and moody. Eight songs were added to the original 10 to increase diversity. The dataset is small and reflects a limited range of musical taste -- it skews toward Western genres and does not include classical, R & B, reggae, or non-English language music. Whose taste the data reflects is unclear, as songs were generated rather than sourced from real listener data. 

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset 



---

## 5. Strengths  

Where does your system seem to work well
The system works well when a user's preferred genre is well-represented in the catalog. Profiles like Chill Lofi Studier and High Energy Pop produced results that matched musical intuition — the top songs were genuinely close matches in both vibe and energy. The scoring logic is fully transparent, meaning every recommendation comes with a clear explanation of exactly why a song scored theway it did. This makes the system easy to debug and understand compared to ablack-box model.


Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition 



---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly.
The genre bonus (+2.0) is so large that it can override all other preferences.A user who wants high-energy ambient music will still receive calm ambient songs at the top because the genre match alone outweighs the energy mismatch. Thiswas confirmed with the Conflicted Listener profile, where Rainy Window (energy: 0.22) ranked above Storm Runner (energy: 0.99) despite the user targeting energy: 0.90. The system also has no concept of mood: sad since that mood does not exist in the dataset, meaning some user preferences will never match anything exactly. Genres like country and folk have only one song each, so users with those preferences will see weak results. The system treats all users as having a single fixed taste and cannot adapt to someone who likes both calm and intense music depending on context.

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.
Five user profiles were tested: Chill Lofi Studier, High Energy Pop, Deep Intense Rock, Conflicted Listener, and EDM Raver. For most profiles the top results matched expectations. The EDM Raver profile produced a near-perfect score of 4.50 for Bass Drop Arena, which was the only song that hit genre,mood, and energy simultaneously. The most surprising result came from the Conflicted Listener profile, which exposed the genre bias — calm ambient songs ranked above high-energy songs despite the user's energy target being 0.90. A weight experiment was also run, reducing genre from +2.0 to +1.0 and doubling energy weight, which confirmed that genre still dominated the rankings even at half strength.


---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes 


- Add a diversity filter so the top 5 results are not all from the same genre
  or artist, even if those songs score highest.
- Replace fixed genre/mood bonuses with a soft similarity score so that related
  genres (like lofi and ambient) receive partial credit instead of zero.
- Add support for multiple taste profiles so the system could recommend music
  for a group rather than a single user.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Building this recommender made it clear how much influence a single design decision — like the genre weight — can have on every result the system produces. What surprised me most was the Conflicted Listener profile: a user asking for high-energy ambient music gets low-energy songs because the system has no way to separate those two preferences. Real platforms like Spotify likely face the same tension but have millions of data points to balance it out. This project changed how I think about recommendation systems — what feels like a smart suggestion is often just math that someone chose, and those choices carry real consequences for what users do and do not get shown.


