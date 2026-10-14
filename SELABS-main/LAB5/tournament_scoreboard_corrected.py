"""Tournament scoreboard for the SE Lab 5 static analysis exercise."""

import secrets
import subprocess
import tempfile

POINTS = {"win": 3, "draw": 1, "loss": 0}
teams = {}
matches = []


def add_team(team_name, players=None):
    """Add a team, giving it an independent list of players."""
    if not isinstance(team_name, str) or not team_name.strip():
        raise ValueError("Team name must be a non-empty string.")
    if team_name in teams:
        raise ValueError(f"Team {team_name!r} already exists.")
    if players is None:
        players = []
    teams[team_name] = {
        "played": 0, "won": 0, "drawn": 0, "lost": 0,
        "gf": 0, "ga": 0, "players": list(players),
    }


def match_result(home_goals, away_goals):
    """Return 'home', 'away', or 'draw' for a valid score."""
    _validate_goals(home_goals, away_goals)
    if home_goals > away_goals:
        return "home"
    if home_goals < away_goals:
        return "away"
    return "draw"


def _validate_goals(home_goals, away_goals):
    """Reject invalid goal counts."""
    for score in (home_goals, away_goals):
        if isinstance(score, bool) or not isinstance(score, int) or score < 0:
            raise ValueError("Goals must be non-negative integers.")


def record_match(home, away, home_goals, away_goals):
    """Record a match after validating teams and goals."""
    if home == away:
        raise ValueError("A team cannot play itself.")
    if home not in teams or away not in teams:
        raise KeyError("Register both teams before recording a match.")
    result = match_result(home_goals, away_goals)
    for team, scored, conceded in (
        (home, home_goals, away_goals),
        (away, away_goals, home_goals),
    ):
        teams[team]["played"] += 1
        teams[team]["gf"] += scored
        teams[team]["ga"] += conceded
    if result == "draw":
        teams[home]["drawn"] += 1
        teams[away]["drawn"] += 1
    else:
        winner, loser = (home, away) if result == "home" else (away, home)
        teams[winner]["won"] += 1
        teams[loser]["lost"] += 1
    matches.append((home, away, home_goals, away_goals))


def points(team_name):
    """Calculate points earned by a registered team."""
    stats = teams[team_name]
    return stats["won"] * POINTS["win"] + stats["drawn"] * POINTS["draw"]


def goal_difference(team_name):
    """Calculate goals for minus goals against."""
    return teams[team_name]["gf"] - teams[team_name]["ga"]


def league_table():
    """Return team names sorted by points and goal difference."""
    return sorted(
        teams,
        key=lambda name: (points(name), goal_difference(name)),
        reverse=True,
    )


def is_top_two(team_name):
    """Return whether a team ranks in the top two."""
    return team_name in league_table()[:2]


def toss_coin():
    """Simulate a coin toss; this is not used for security decisions."""
    return secrets.choice(("Heads", "Tails"))


def table_file_path():
    """Safely create a unique temporary file."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        return temp_file.name


def publish_table(server):
    """Copy the table to a validated host without a shell."""
    if not isinstance(server, str) or not server.strip():
        raise ValueError("Server must be a non-empty hostname.")
    if any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-" for char in server):
        raise ValueError("Server contains invalid hostname characters.")
    subprocess.run(
        ["scp", "table.json", f"{server}:/var/www/"],
        check=True,
        shell=False,
    )


def main():
    """Run a sample tournament and print its standings."""
    for name in ("Royal Strikers", "City Rovers", "Lake United", "Hill Warriors"):
        add_team(name)
    print("Toss:", toss_coin())
    record_match("Royal Strikers", "City Rovers", 2, 1)
    record_match("Lake United", "Hill Warriors", 0, 0)
    record_match("City Rovers", "Lake United", 3, 2)
    record_match("Hill Warriors", "Royal Strikers", 1, 1)

    print("Pos Team Played Won Drawn Lost Pts")
    for position, name in enumerate(league_table(), start=1):
        stats = teams[name]
        print(
            position, name, stats["played"], stats["won"],
            stats["drawn"], stats["lost"], points(name),
        )
    print("Is City Rovers in the top two?", is_top_two("City Rovers"))
    print("Matches played:", len(matches))


if __name__ == "__main__":
    main()
