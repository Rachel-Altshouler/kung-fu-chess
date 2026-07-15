import unittest
from model.board import ChessBoard
from game_io.board_printer import BoardPrinter


class TestBoardPrinter(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()

    def test_canonical_representation(self):
        self.board.set_grid([
            ['wK', '.', 'bK'],
            ['.', 'wN', '.'],
            ['bP', '.', 'wR']
        ])
        expected_output = "wK . bK\n. wN .\nbP . wR"
        self.assertEqual(
            BoardPrinter.get_canonical_representation(self.board),
            expected_output,
        )

    def test_empty_board(self):
        self.board.set_grid([['.', '.'], ['.', '.']])
        self.assertEqual(
            BoardPrinter.get_canonical_representation(self.board),
            ". .\n. .",
        )
