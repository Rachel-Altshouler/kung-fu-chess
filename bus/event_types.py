from enum import Enum


class Events(Enum):
    SCORE_UPDATED = "score_updated"
    MOVE_LOGGED = "move_logged"
    PIECE_MOVED = "piece_moved"
    PIECE_CAPTURED = "piece_captured"
    GAME_STARTED = "game_started"
    GAME_ENDED = "game_ended"
