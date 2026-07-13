class BoardConstants:
    CELL_SIZE = 100
    EMPTY_CELL = "."
    MS_PER_SQUARE = 100
    MS_KNIGHT_JUMP = 1000

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