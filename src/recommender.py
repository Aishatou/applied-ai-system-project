import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "target_valence" : 0.5
        }
        scored = []
        for song in self.songs: 
            song_dict = {
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "valence": song.valence, 
                "title" : song.title
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((song, score))
        scored.sort(key=lambda x: x[1], reverse=True)

        return [song for song, score in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        reasons = [] 
        if song.genre == user.favorite_genre:
            reasons.append(f"genre match ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood match ({song.mood})")
        energy_gap = abs(song.energy - user.target_energy)
        if energy_gap < 0.2:
            reasons.append(f"energy is close to your target ({song.energy:.2f})")
        if not reasons : 
            return "No strong match, but included for variety !"
        return "Recommended because of " + ", ".join(reasons)
    

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    # TODO: Implement CSV loading logic
    songs = [] 
    with open(csv_path, newline = "", encoding = "utf-8") as f: 
        reader = csv.DictReader(f)
        for row in reader: 
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)

    #print(f"Loading songs from {csv_path}...")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    score = 0.0 
    reasons = [] 


    # Genre Match 
    if song.get("genre") == user_prefs.get("favorite_genre"):
        score += 2.0 
        reasons.append(f"genre match (+2.0)")
    
    # Mood Match 
    if song.get("mood") == user_prefs.get("favorite_mood"):
        score += 1.0
        reasons.append(f"mood match (+1.0)")
    
    #Energy Similarity 
    energy_score = 1.0 - abs(song.get("energy", 0 ) - user_prefs.get("target_energy", 0))
    score += energy_score
    reasons.append(f"energy similarity (+{energy_score:.2f})")

    # Valence Similarity
    valence_score = (1.0 - abs(song.get("valence", 0) - user_prefs.get("target_valence", 0.5))) * 0.5 
    score += valence_score 
    reasons.append(f"valence similarity (+{valence_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    
    scored = []
    for song in songs : 
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, reasons))
    scored.sort(key = lambda x: x[1], reverse= True)
    return scored[:k]

