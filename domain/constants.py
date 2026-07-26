class BoardConstants:
    CELL_SIZE = 100
    PIECE_CELL_RATIO = 0.88
    EMPTY_CELL = "."
    MS_PER_SQUARE = 500  # walk pace — a bit faster than 700ms/sq
    MS_KNIGHT_JUMP = 1000
    MOVE_COOLDOWN_MS = 500


class Colors:
    WHITE = "w"
    BLACK = "b"

class PieceTypes:
    KING = "K"
    ROOK = "R"
    BISHOP = "B"
    QUEEN = "Q"
    KNIGHT = "N"
    PAWN = "P"

class GraphicsConstants:
    HEADER_HEIGHT = 80
    FOOTER_HEIGHT = 40
    DISPLAY_CELL_SIZE = 80
    FRAME_DELAY_MS = 30
    WINDOW_NAME = "KungFu Chess"
    SIDE_PANEL_WIDTH = 210
    MOVE_LOG_LINE_HEIGHT = 18
    MOVE_LOG_MAX_LINES = 20


class ScoreConstants:
    PIECE_CAPTURE_SECONDS = {
        PieceTypes.PAWN: 1,
        PieceTypes.KNIGHT: 3,
        PieceTypes.BISHOP: 3,
        PieceTypes.ROOK: 5,
        PieceTypes.QUEEN: 9,
        PieceTypes.KING: 0,
    }

class InputHeaders:
    BOARD_HEADER = "Board:"
    COMMANDS_HEADER = "Commands:"

class Commands:
    CLICK = "click"
    WAIT = "wait"
    JUMP = "jump"
    PRINT_BOARD = "print board"

class MoveResult:
    OK = "ok"
    OUTSIDE_BOARD = "outside_board"
    EMPTY_SOURCE = "empty_source"
    FRIENDLY_DESTINATION = "friendly_destination"
    ILLEGAL_PIECE_MOVE = "illegal_piece_move"
class subscribers:
    START_FRAMES = 45
    END_FRAMES = 90