"""
agent_main.py — Interactive entry point for the MoodMatcher Agentic System.

Run with:
    python agent_main.py

The agent accepts free-text vibe descriptions and runs the full
Plan → Act → Evaluate → Refine loop for each one.
"""

from src.agent import MusicAgent


# ---------------------------------------------------------------------------
# Demo vibes — used when running the script directly.
# These match the required 2–3 sample interactions for the portfolio README.
# ---------------------------------------------------------------------------
DEMO_VIBES = [
    "sad late night energy, something slow and moody to zone out to",
    "I need maximum hype for the gym, nothing but high energy bangers",
    "chill Sunday morning, coffee in hand, lo-fi and relaxed vibes",
]


def run_demo(agent: MusicAgent) -> None:
    """Runs the agent against all demo vibe prompts."""
    print("\n" + "=" * 58)
    print("  MoodMatcher Agent — Demo Run")
    print("=" * 58)
    for vibe in DEMO_VIBES:
        agent.run(vibe)


def run_interactive(agent: MusicAgent) -> None:
    """Lets the user type their own vibe at the terminal."""
    print("\n" + "=" * 58)
    print("  MoodMatcher Agent — Interactive Mode")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 58)
    while True:
        vibe = input("\n  Describe your vibe: ").strip()
        if vibe.lower() in ("quit", "exit", "q"):
            print("  Bye! 🎧")
            break
        if not vibe:
            print("  Please enter a vibe description.")
            continue
        agent.run(vibe)


def main() -> None:
    agent = MusicAgent(catalog_path="data/songs.csv")

    print("\nChoose a mode:")
    print("  1 — Run demo (3 preset vibes)")
    print("  2 — Interactive (type your own vibe)")
    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "2":
        run_interactive(agent)
    else:
        run_demo(agent)


if __name__ == "__main__":
    main()
