import json
import os


HIGHSCORE_FILE = "reaction_highscores.json"
OLD_HIGHSCORE_FILE = "reaction_highscores.txt"
OLD_SEPARATOR = " / "


def load_scores(game=None):
    migrate_old_scores()

    if not os.path.exists(HIGHSCORE_FILE):
        return []

    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    scores = []
    for item in data.get("scores", []):
        score = normalize_score(item)
        if score and (game is None or score["game"] == game):
            scores.append(score)

    return sorted(scores, key=lambda score: score["time"])


def add_score(player, game, time_ms):
    scores = load_scores()
    scores.append(
        {
            "player": (player or "Unbekannt").strip(),
            "game": (game or "Unbekannt").strip(),
            "time": round(float(time_ms), 1),
        }
    )
    save_scores(scores)


def save_scores(scores):
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as file:
        json.dump({"scores": scores}, file, indent=2, ensure_ascii=False)


def normalize_score(item):
    try:
        return {
            "player": str(item.get("player") or "Unbekannt"),
            "game": str(item.get("game") or "Unbekannt"),
            "time": float(item.get("time")),
        }
    except (AttributeError, TypeError, ValueError):
        return None


def migrate_old_scores():
    if os.path.exists(HIGHSCORE_FILE) or not os.path.exists(OLD_HIGHSCORE_FILE):
        return

    scores = []
    with open(OLD_HIGHSCORE_FILE, "r", encoding="utf-8") as file:
        for line in file:
            score = parse_old_score_line(line)
            if score:
                scores.append(score)

    save_scores(scores)


def parse_old_score_line(line):
    parts = [part.strip() for part in line.strip().split(OLD_SEPARATOR)]

    if len(parts) == 3:
        player, game, time_text = parts
        try:
            return {
                "player": player or "Unbekannt",
                "game": game or "Farb-Reaktion",
                "time": round(float(time_text), 1),
            }
        except ValueError:
            return None

    if len(parts) == 1 and parts[0]:
        try:
            return {
                "player": "Unbekannt",
                "game": "Farb-Reaktion",
                "time": round(float(parts[0]), 1),
            }
        except ValueError:
            return None

    return None
