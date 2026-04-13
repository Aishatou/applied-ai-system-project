"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

def run_profile(profile_name: str, user_prefs: dict, songs: list) -> None:
    """Runs the recommender for a given profile and prints formatted results."""
    print(f"\n{'='*50}")
    print(f"Profile: {profile_name}")
    print(f"Genre: {user_prefs['favorite_genre']} | Mood: {user_prefs['favorite_mood']} | Energy: {user_prefs['target_energy']}")
    print(f"{'='*50}")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    for i, (song, score, reasons) in enumerate(recommendations, 1):
        print(f"\n#{i} {song['title']} by {song['artist']}")
        print(f"    Score : {score:.2f}")
        print(f"    Why   : {', '.join(reasons)}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    profiles = [
        (
            "Chill Lofi Studier",
            {
                "favorite_genre": "lofi",
                "favorite_mood": "chill",
                "target_energy": 0.40,
                "target_valence": 0.58
            }
        ),
        (
            "High Energy Pop",
            {
                "favorite_genre": "pop",
                "favorite_mood": "happy",
                "target_energy": 0.85,
                "target_valence": 0.82
            }
        ),
        (
            "Deep Intense Rock",
            {
                "favorite_genre": "rock",
                "favorite_mood": "intense",
                "target_energy": 0.90,
                "target_valence": 0.45
            }
        ),
        (
            "Conflicted Listener",
            {
                "favorite_genre": "ambient",
                "favorite_mood": "sad",
                "target_energy": 0.90,
                "target_valence": 0.20
            }
        ),
        (
            "EDM Raver",
            {
                "favorite_genre": "edm",
                "favorite_mood": "intense",
                "target_energy": 0.95,
                "target_valence": 0.52
            }
        ),
    ]
    
    

    for profile_name, user_prefs in profiles:
        run_profile(profile_name, user_prefs, songs)

















#def main() -> None:
   # songs = load_songs("data/songs.csv") 

    # Starter example profile
    #user_prefs = {
        #"favorite_genre" : "lofi", 
        #"favorite_mood" : "chill",
        #"target_energy" : 0.40,
        #"target_valence" : 0.58
        #  }
    #user_prefs = {
        #"favorite_genre" : "pop",
       # "favorite_mood" : "happy",
       # "target_energy" : 0.85, 
        #"target_valence" : 0.82
       # }
    
    #user_prefs = {
       # "favorite_genre" : "rock",
       # "favorite_mood" : "intense",
       # "target_energy" : 0.90, 
       # "target_valence" : 0.45
    #}


   # recommendations = recommend_songs(user_prefs, songs, k=5)

    #print("\nTop recommendations:\n")
   # for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        #song, score, explanation = rec
        #print(f"{song['title']} - Score: {score:.2f}")
        #print(f"Because: {explanation}")
        #print()



if __name__ == "__main__":
    main()
