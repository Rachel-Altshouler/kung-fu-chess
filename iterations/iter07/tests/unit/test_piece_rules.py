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

    def test_white_pawn_moves_up(self):
        grid = [['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(grid, (1, 1), (0, 1), 'w'))

    def test_black_pawn_moves_down(self):
        grid = [['.', 'bP', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(grid, (0, 1), (1, 1), 'b'))

    def test_white_pawn_captures_diagonally(self):
        grid = [['.', '.', 'bK'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(grid, (1, 1), (0, 2), 'w'))
        grid_left = [['bK', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(grid_left, (1, 1), (0, 0), 'w'))

    def test_black_pawn_captures_diagonally(self):
        grid = [['.', 'bP', '.'], ['wK', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(grid, (0, 1), (1, 0), 'b'))

    def test_pawn_two_square_from_start_when_path_clear(self):
        white_grid = [['.', '.', '.'], ['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(white_grid, (2, 1), (0, 1), 'w'))
        black_grid = [['.', 'bP', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertTrue(PieceRules.is_pawn_move(black_grid, (0, 1), (2, 1), 'b'))

    def test_pawn_two_square_blocked_when_path_not_clear(self):
        grid = [['.', '.', '.'], ['.', 'wR', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (2, 1), (0, 1), 'w'))

    def test_pawn_cannot_move_two_squares_after_leaving_start(self):
        grid = [['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (3, 1), 'w'))
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (2, 1), 'w'))

    def test_pawn_cannot_move_two_squares_in_wrong_direction(self):
        grid = [['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (2, 1), 'w'))
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (3, 1), 'w'))

    def test_pawn_cannot_capture_forward(self):
        grid = [['.', 'bK', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (0, 1), 'w'))

    def test_pawn_cannot_move_diagonally_to_empty(self):
        grid = [['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (0, 0), 'w'))

    def test_white_pawn_cannot_move_down(self):
        grid = [['.', '.', '.'], ['.', 'wP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (2, 1), 'w'))

    def test_black_pawn_cannot_move_up(self):
        grid = [['.', '.', '.'], ['.', 'bP', '.'], ['.', '.', '.']]
        self.assertFalse(PieceRules.is_pawn_move(grid, (1, 1), (0, 1), 'b'))
