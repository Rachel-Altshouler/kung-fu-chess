import unittest

from domain.board import ChessBoard
from domain.constants import Colors
from rules.endgame import EndgameRules


class TestEndgameRules(unittest.TestCase):
    def test_king_in_check(self):
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "bK"],
            [".", ".", "."],
            ["wK", ".", "."],
        ])
        self.assertTrue(EndgameRules.is_in_check(board, Colors.BLACK))

    def test_king_not_in_check(self):
        board = ChessBoard()
        board.set_grid([
            ["wK", ".", "."],
            [".", ".", "bK"],
            [".", ".", "."],
        ])
        self.assertFalse(EndgameRules.is_in_check(board, Colors.BLACK))

    def test_check_threat_does_not_end_game(self):
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "bK"],
            [".", ".", "."],
            ["wK", ".", "."],
        ])
        self.assertIsNone(EndgameRules.evaluate(board))

    def test_checkmate_position_does_not_end_game(self):
        board = ChessBoard()
        board.set_grid([
            [".", "wR", "bK"],
            ["wK", "wR", "."],
            [".", ".", "."],
        ])
        self.assertIsNone(EndgameRules.evaluate(board))

    def test_stalemate_position_does_not_end_game(self):
        board = ChessBoard()
        grid = [["." for _ in range(8)] for _ in range(8)]
        grid[0][2] = "bK"
        grid[2][1] = "wQ"
        grid[2][2] = "wK"
        board.set_grid(grid)
        self.assertIsNone(EndgameRules.evaluate(board))

    def test_king_captured_ends_game(self):
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "."],
            [".", ".", "."],
            ["wK", ".", "."],
        ])
        result = EndgameRules.evaluate(board)
        self.assertEqual(result, ("king_captured", Colors.WHITE))

    def test_move_into_check_is_illegal(self):
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "bK"],
            [".", ".", "."],
            ["wK", ".", "."],
        ])
        self.assertFalse(EndgameRules.is_legal_move(board, (0, 2), (0, 1)))


if __name__ == "__main__":
    unittest.main()
