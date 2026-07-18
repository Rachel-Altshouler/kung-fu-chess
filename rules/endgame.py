from model.constants import BoardConstants, Colors
from model.piece import Piece
from rules.piece_rules import PieceRules
from rules.rule_engine import RuleEngine


class EndgameRules:
    @staticmethod
    def find_king(board, color):
        for piece_data in board.get_all_pieces():
            piece = Piece.from_token(piece_data["token"])
            if (
                piece is not None
                and piece.color == color
                and piece.piece_type == "K"
            ):
                return piece_data["pos"]
        return None

    @staticmethod
    def _pawn_attacks_square(color, source, target):
        source_row, source_col = source
        target_row, target_col = target
        forward = -1 if color == Colors.WHITE else 1
        return (
            target_row == source_row + forward
            and abs(target_col - source_col) == 1
        )
    #האם משבצת תחת איום
    @staticmethod
    def is_square_attacked(board, row, col, attacker_color):
        grid = board.get_grid()
        target = (row, col)
        target_token = grid[row][col]
        target_piece = Piece.from_token(target_token)

        for source_row in range(len(grid)):
            for source_col in range(len(grid[0])):
                token = grid[source_row][source_col]
                piece = Piece.from_token(token)
                if piece is None or piece.color != attacker_color:
                    continue

                source = (source_row, source_col)
                if piece.piece_type == "P":
                    if EndgameRules._pawn_attacks_square(
                        piece.color,
                        source,
                        target,
                    ):
                        return True
                    continue

                if not PieceRules.is_piece_move_valid(
                    grid,
                    piece.piece_type,
                    source,
                    target,
                    piece.color,
                ):
                    continue

                if (
                    target_piece is not None
                    and piece.is_same_color(target_piece)
                ):
                    continue
                return True
        return False

    #האם המלך במט
    @staticmethod
    def is_in_check(board, color):
        king_pos = EndgameRules.find_king(board, color)
        if king_pos is None:
            return True

        opponent = (
            Colors.BLACK if color == Colors.WHITE else Colors.WHITE
        )
        row, col = king_pos
        return EndgameRules.is_square_attacked(board, row, col, opponent)

    @staticmethod
    def _apply_move(board, source, destination):
        captured = board.get_piece_at(destination)
        board.move_piece(source, destination)
        return captured

    @staticmethod
    def _undo_move(board, source, destination, captured):
        piece = board.get_piece_at(destination)
        board.set_piece_at(source, piece)
        board.set_piece_at(destination, captured)

    @staticmethod
    def is_legal_move(board, source, destination):
        if not RuleEngine.is_valid_move(board, source, destination):
            return False

        source_token = board.get_piece_at(source)
        mover = Piece.from_token(source_token)
        if mover is None:
            return False

        captured = EndgameRules._apply_move(board, source, destination)
        in_check = EndgameRules.is_in_check(board, mover.color)
        EndgameRules._undo_move(board, source, destination, captured)
        return not in_check

    #האם יש לפחות מהלך חוקי אחד
    @staticmethod
    def has_legal_move(board, color):
        for piece_data in board.get_all_pieces():
            piece = Piece.from_token(piece_data["token"])
            if piece is None or piece.color != color:
                continue

            source = piece_data["pos"]
            grid = board.get_grid()
            for row in range(len(grid)):
                for col in range(len(grid[0])):
                    if EndgameRules.is_legal_move(board, source, (row, col)):
                        return True
        return False

    @staticmethod
    def king_has_legal_move(board, color):
        king_pos = EndgameRules.find_king(board, color)
        if king_pos is None:
            return False

        grid = board.get_grid()
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if EndgameRules.is_legal_move(board, king_pos, (row, col)):
                    return True
        return False

    @staticmethod
    def evaluate(board):
        for color in (Colors.WHITE, Colors.BLACK):
            if EndgameRules.find_king(board, color) is None:
                continue

            in_check = EndgameRules.is_in_check(board, color)
            if in_check:
                opponent = (
                    Colors.BLACK if color == Colors.WHITE else Colors.WHITE
                )
                return "checkmate", opponent

            if not EndgameRules.has_legal_move(board, color):
                return "stalemate", None
        return None
