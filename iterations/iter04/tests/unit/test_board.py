import unittest
from model.board import ChessBoard


class TestChessBoard(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])

    def test_get_and_set_piece(self):
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.board.set_piece_at((1, 1), 'wR')
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wR')

    def test_is_empty(self):
        self.assertFalse(self.board.is_empty((0, 0)))
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_is_within_bounds(self):
        self.assertTrue(self.board.is_within_bounds(0, 0))
        self.assertFalse(self.board.is_within_bounds(5, 5))

    def test_is_within_bounds_empty_grid(self):
        board = ChessBoard()
        self.assertFalse(board.is_within_bounds(0, 0))

    def test_get_piece_with_position_object(self):
        from model.position import Position
        self.assertEqual(self.board.get_piece_at(Position(0, 0)), 'wK')

    def test_move_piece(self):
        self.board.move_piece((0, 0), (1, 1))
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertEqual(self.board.get_piece_at((0, 0)), '.')
