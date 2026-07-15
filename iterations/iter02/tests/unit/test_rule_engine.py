import unittest
from model.board import ChessBoard
from rules.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])

    def test_are_same_color(self):
        self.assertTrue(RuleEngine.are_same_color(self.board, (0, 0), (0, 1)))
        self.assertFalse(RuleEngine.are_same_color(self.board, (0, 0), (2, 2)))

    def test_valid_king_move(self):
        self.assertTrue(RuleEngine.is_valid_move(self.board, (0, 0), (1, 1)))
        self.assertFalse(RuleEngine.is_valid_move(self.board, (0, 0), (0, 2)))

    def test_cannot_capture_friendly_piece(self):
        self.assertFalse(RuleEngine.is_valid_move(self.board, (0, 0), (0, 1)))

    def test_are_same_color_with_empty_cell(self):
        self.assertFalse(RuleEngine.are_same_color(self.board, (0, 0), (1, 1)))

    def test_invalid_move_out_of_bounds(self):
        self.assertFalse(RuleEngine.is_valid_move(self.board, (0, 0), (5, 5)))

    def test_invalid_move_from_empty_source(self):
        self.assertFalse(RuleEngine.is_valid_move(self.board, (1, 1), (0, 0)))

    def test_valid_move_with_position_object(self):
        from model.position import Position
        self.assertTrue(RuleEngine.is_valid_move(
            self.board, Position(0, 0), Position(1, 1)
        ))
