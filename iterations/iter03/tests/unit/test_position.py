import unittest
from model.position import Position
from model.piece import Piece


class TestPosition(unittest.TestCase):
    def test_as_tuple(self):
        position = Position(1, 2)
        self.assertEqual(position.as_tuple(), (1, 2))

    def test_equality_with_position(self):
        self.assertEqual(Position(0, 0), Position(0, 0))

    def test_equality_with_tuple(self):
        self.assertEqual(Position(2, 3), (2, 3))

    def test_equality_with_invalid_type(self):
        self.assertFalse(Position(0, 0) == "invalid")

    def test_repr(self):
        self.assertEqual(repr(Position(1, 2)), "Position(1, 2)")

    def test_piece_from_token(self):
        piece = Piece.from_token('wK')
        self.assertEqual(piece.color, 'w')
        self.assertEqual(piece.piece_type, 'K')

    def test_piece_from_empty_token(self):
        self.assertIsNone(Piece.from_token('.'))

    def test_piece_to_token(self):
        self.assertEqual(Piece('b', 'Q').to_token(), 'bQ')

    def test_piece_is_same_color(self):
        white_king = Piece('w', 'K')
        white_rook = Piece('w', 'R')
        black_king = Piece('b', 'K')
        self.assertTrue(white_king.is_same_color(white_rook))
        self.assertFalse(white_king.is_same_color(black_king))
