import secrets
import string
import random
from typing import Optional, Dict, List, Tuple, Any

# In-memory storage
games: Dict[str, Dict[str, Any]] = {}
player_to_game: Dict[str, str] = {}


def generate_game_code() -> str:
    """Generate unique 6-character game code (uppercase + digits)"""
    while True:
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        if code not in games:
            return code


def create_game(host_name: str, timer_enabled: bool, timer_seconds: int, host_sid: str) -> str:
    """Create a new game and return game code"""
    code = generate_game_code()
    games[code] = {
        "code": code,
        "host_sid": host_sid,
        "host_name": host_name,
        "players": {
            host_sid: {"name": host_name, "score": 0, "connected": True}
        },
        "settings": {
            "timer_enabled": timer_enabled,
            "timer_seconds": timer_seconds
        },
        "phase": "lobby",
        "questions": [],
        "current_question_index": 0,
        "question_order": [],
        "players_ready": set(),
        "timer_start": None,
        "advanced_from_winner": False
    }
    player_to_game[host_sid] = code
    return code


def join_game(game_code: str, player_name: str, sid: str) -> Tuple[bool, str]:
    """
    Join a game. Returns (success, error_message)
    Handles both new joins and reconnections.
    """
    if game_code not in games:
        return False, "Game not found"

    game = games[game_code]

    # Check if this is a reconnection (same name exists)
    for player_sid, player_data in game["players"].items():
        if player_data["name"] == player_name:
            # Reconnection
            if player_data["connected"]:
                return False, "Name already taken"
            else:
                # Update sid and mark as connected
                old_sid = player_sid
                game["players"][sid] = game["players"].pop(old_sid)
                game["players"][sid]["connected"] = True
                player_to_game[sid] = game_code
                if old_sid in player_to_game:
                    del player_to_game[old_sid]
                # Update host_sid if needed
                if game["host_sid"] == old_sid:
                    game["host_sid"] = sid
                return True, ""

    # New player
    if len(game["players"]) >= 10:  # Max players limit
        return False, "Game is full"

    game["players"][sid] = {"name": player_name, "score": 0, "connected": True}
    player_to_game[sid] = game_code
    return True, ""


def disconnect_player(sid: str):
    """Mark a player as disconnected"""
    if sid in player_to_game:
        game_code = player_to_game[sid]
        if game_code in games and sid in games[game_code]["players"]:
            games[game_code]["players"][sid]["connected"] = False


def get_game(sid: str) -> Optional[Dict[str, Any]]:
    """Get game for a player"""
    if sid in player_to_game:
        game_code = player_to_game[sid]
        return games.get(game_code)
    return None


def is_host(sid: str, game_code: str) -> bool:
    """Check if player is game host"""
    return game_code in games and games[game_code]["host_sid"] == sid


def get_players_list(game_code: str) -> List[Dict[str, Any]]:
    """Get list of players with their status"""
    if game_code not in games:
        return []

    game = games[game_code]
    return [
        {
            "name": data["name"],
            "score": data["score"],
            "connected": data["connected"],
            "is_host": sid == game["host_sid"]
        }
        for sid, data in game["players"].items()
    ]


def submit_question(game_code: str, sid: str, question_text: str, doodle_data: str):
    """Submit a question for the game"""
    if game_code not in games:
        return False

    game = games[game_code]
    if sid not in game["players"]:
        return False

    # Check if player already submitted a question
    author = game["players"][sid]["name"]
    for existing_q in game["questions"]:
        if existing_q["author"] == author:
            # Player already submitted, don't add duplicate
            game["players_ready"].add(sid)
            return True

    game["questions"].append({
        "author": author,
        "text": question_text,
        "doodle": doodle_data,
        "answers": {},
        "points_awarded": False
    })
    game["players_ready"].add(sid)
    return True


def start_answering(game_code: str) -> bool:
    """Randomize question order and start answering phase"""
    if game_code not in games:
        return False

    game = games[game_code]
    if not game["questions"]:
        return False

    # Randomize question order
    indices = list(range(len(game["questions"])))
    random.shuffle(indices)
    game["question_order"] = indices
    game["current_question_index"] = 0
    game["phase"] = "answering"
    game["players_ready"] = set()

    return True


def get_current_question(game_code: str) -> Optional[Dict[str, Any]]:
    """Get the current question being answered"""
    if game_code not in games:
        return None

    game = games[game_code]
    if game["phase"] != "answering":
        return None

    if game["current_question_index"] >= len(game["question_order"]):
        return None

    question_idx = game["question_order"][game["current_question_index"]]
    return game["questions"][question_idx]


def submit_answer(game_code: str, sid: str, answer: float) -> bool:
    """Submit an answer to current question"""
    if game_code not in games:
        return False

    game = games[game_code]
    if sid not in game["players"]:
        return False

    if game["phase"] != "answering":
        return False

    if game["current_question_index"] >= len(game["question_order"]):
        return False

    question_idx = game["question_order"][game["current_question_index"]]
    player_name = game["players"][sid]["name"]

    # Only add answer if player hasn't already answered
    # (This allows updating answer, but prevents multiple submissions)
    game["questions"][question_idx]["answers"][player_name] = answer
    game["players_ready"].add(sid)

    return True


def calculate_winner(answers: Dict[str, float]) -> Tuple[List[str], List[Dict[str, Any]], float]:
    """
    Calculate winners based on median.
    Returns: (winners, sorted_results, median_value)

    sorted_results: [{"name": str, "answer": float, "is_winner": bool}, ...]
    """
    if not answers:
        return [], [], 0

    values = sorted([(name, float(ans)) for name, ans in answers.items()],
                    key=lambda x: x[1])
    n = len(values)

    if n % 2 == 1:
        # Odd number: median is middle value
        median_idx = n // 2
        median = values[median_idx][1]
        winning_answer = median
    else:
        # Even number: median is average of two middle values
        mid1, mid2 = values[n//2 - 1][1], values[n//2][1]
        median = (mid1 + mid2) / 2
        mean = sum(v[1] for v in values) / n

        dist1 = abs(mid1 - mean)
        dist2 = abs(mid2 - mean)

        if dist1 < dist2:
            winning_answer = mid1
        elif dist2 < dist1:
            winning_answer = mid2
        else:
            winning_answer = (mid1, mid2)  # both win

    # Find winners
    if isinstance(winning_answer, tuple):
        winners = [n for n, v in values if v in winning_answer]
    else:
        winners = [n for n, v in values if v == winning_answer]

    # Build results
    sorted_results = [
        {"name": n, "answer": v, "is_winner": n in winners}
        for n, v in values
    ]

    return winners, sorted_results, median


def award_points(game_code: str, winners: List[str]):
    """Award 1 point to each winner"""
    if game_code not in games:
        return

    game = games[game_code]
    for sid, player_data in game["players"].items():
        if player_data["name"] in winners:
            player_data["score"] += 1


def get_leaderboard(game_code: str) -> List[Dict[str, Any]]:
    """Get current leaderboard sorted by score"""
    if game_code not in games:
        return []

    game = games[game_code]
    scores = [
        {"name": data["name"], "score": data["score"]}
        for data in game["players"].values()
    ]
    return sorted(scores, key=lambda x: x["score"], reverse=True)


def advance_to_next_question(game_code: str) -> bool:
    """
    Advance to next question or end game.
    Returns True if there are more questions, False if game is over.
    """
    if game_code not in games:
        return False

    game = games[game_code]
    game["current_question_index"] += 1
    game["players_ready"] = set()

    if game["current_question_index"] >= len(game["question_order"]):
        game["phase"] = "final"
        return False

    return True


def get_ready_players(game_code: str) -> List[str]:
    """Get list of players who are ready"""
    if game_code not in games:
        return []

    game = games[game_code]
    return [
        game["players"][sid]["name"]
        for sid in game["players_ready"]
        if sid in game["players"]
    ]


def cleanup_game(game_code: str):
    """Remove a game and clean up player mappings"""
    if game_code in games:
        game = games[game_code]
        # Remove player mappings
        for sid in list(game["players"].keys()):
            if sid in player_to_game:
                del player_to_game[sid]
        # Remove game
        del games[game_code]
