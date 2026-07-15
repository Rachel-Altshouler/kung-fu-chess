import unittest
from rules.piece_rules import PieceRules

class TestPieceRules(unittest.TestCase):

    def setUp(self):
        self.grid = [['wR', 'wP', '.'], ['.', '.', '.'], ['.', '.', '.']]

    def test_is_path_blocked(self):
        self.assertTrue(PieceRules.is_path_blocked(self.grid, (0, 0), (0, 2)))
        self.assertFalse(PieceRules.is_path_blocked(self.grid, (0, 0), (0, 1)))

    def test_king_move(self):
        self.assertTrue(PieceRules.is_king_move((0, 0), (1, 1)))
        self.assertFalse(PieceRules.is_king_move((0, 0), (0, 2)))

    def test_rook_move(self):
        grid = [['wR', '.', '.'], ['wP', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_rook_move(grid, (0, 0), (0, 2)))
        self.assertFalse(PieceRules.is_rook_move(grid, (0, 0), (2, 0)))
        self.assertFalse(PieceRules.is_rook_move(grid, (0, 0), (1, 1)))

    def test_bishop_move(self):
        clear_grid = [['wB', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_bishop_move(clear_grid, (0, 0), (2, 2)))
        blocked_grid = [['wB', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_bishop_move(blocked_grid, (0, 0), (2, 2)))
        self.assertFalse(PieceRules.is_bishop_move(clear_grid, (0, 0), (0, 2)))

    def test_piece_move_valid_for_each_type(self):
        grid = [['wB', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_piece_move_valid(grid, 'B', (0, 0), (2, 2), 'w'))
        queen_grid = [['wQ', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_piece_move_valid(queen_grid, 'Q', (0, 0), (0, 2), 'w'))

    def test_queen_move(self):
        grid = [['wQ', '.', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_queen_move(grid, (0, 0), (0, 2)))
        self.assertTrue(PieceRules.is_queen_move(grid, (0, 0), (2, 2)))
        self.assertFalse(PieceRules.is_queen_move(grid, (0, 0), (1, 2)))

    def test_knight_move(self):
        self.assertTrue(PieceRules.is_knight_move((0, 0), (1, 2)))
        self.assertTrue(PieceRules.is_knight_move((0, 0), (2, 1)))
        self.assertFalse(PieceRules.is_knight_move((0, 0), (2, 2)))

    def test_knight_jumps_over_blocker(self):
        blocked_grid = [['wN', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_piece_move_valid(blocked_grid, 'N', (0, 0), (1, 2), 'w'))
