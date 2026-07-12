import unittest
from model.board import ChessBoard
from game_io.board_printer import BoardPrinter


class TestBoardPrinter(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()

    def test_canonical_representation(self):
        # מגדירים לוח ידנית
        self.board.set_grid([
            ['wK', '.', 'bK'],
            ['.', 'wN', '.'],
            ['bP', '.', 'wR']
        ])

        # התוצאה הצפויה מהמדפיס
        expected_output = "wK . bK\n. wN .\nbP . wR"

        # בדיקה שהפלט תואם בדיוק
        actual_output = BoardPrinter.get_canonical_representation(self.board)
        self.assertEqual(actual_output, expected_output)

    def test_empty_board(self):
        # בדיקה של לוח ריק (מקרה קצה)
        self.board.set_grid([['.', '.'], ['.', '.']])
        expected_output = ". .\n. ."
        self.assertEqual(BoardPrinter.get_canonical_representation(self.board), expected_output)


if __name__ == '__main__':
    unittest.main()