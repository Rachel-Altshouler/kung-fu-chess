from model.piece import Piece
from rules.piece_rules import PieceRules


class RuleEngine:
    @staticmethod

    def _to_coords(position):
        if hasattr(position, 'as_tuple'):
            return position.as_tuple()
        return position[0], position[1]

    @staticmethod
    #בודקת אם הכלים באותו צבע
    def are_same_color(board, first_position, second_position) -> bool:
        first_piece = Piece.from_token(board.get_piece_at(first_position))
        second_piece = Piece.from_token(board.get_piece_at(second_position))
        if first_piece is None or second_piece is None:
            return False
        return first_piece.is_same_color(second_piece)

    @staticmethod
    #בודקת אם המהלך חוקי-גבולות מקור לא ריק לא לכידת חבר וחוקי תנועת הכלי
    def is_valid_move(board, source_position, destination_position) -> bool:
        source_coords = RuleEngine._to_coords(source_position)
        destination_coords = RuleEngine._to_coords(destination_position)

        if not board.is_within_bounds(*source_coords) or not board.is_within_bounds(*destination_coords):
            return False

        source_token = board.get_piece_at(source_coords)
        if source_token == '.':
            return False

        destination_token = board.get_piece_at(destination_coords)
        source_piece = Piece.from_token(source_token)
        destination_piece = Piece.from_token(destination_token)

        if destination_piece is not None and source_piece.is_same_color(destination_piece):
            return False

        return PieceRules.is_piece_move_valid(
            board.get_grid(),
            source_piece.piece_type,
            source_coords,
            destination_coords,
            source_piece.color,
        )
