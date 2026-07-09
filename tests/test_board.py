import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from board import ChessBoard

class TestChessBoard(unittest.TestCase):

    def test_board_loading_and_printing(self):
        """בדיקת טעינה והדפסה רגילה"""
        input_data = ["Board:", "wR .", ". bP", "Commands:", "print board"]
        board = ChessBoard()
        self.assertTrue(board.load_from_text_lines(input_data))
        self.assertEqual(board.get_canonical_representation(), "wR .\n. bP")

    def test_loading_invalid_board(self):
        """בודק את השורות בלוח שמטפלות בשגיאות טעינה (מעלה אחוזי כיסוי!)"""
        invalid_input = ["Board:", "wR .", "wX", "Commands:"] # wX לא חוקי
        board = ChessBoard()
        self.assertFalse(board.load_from_text_lines(invalid_input))

    def test_wait_command_updates_time(self):
        input_data = ["Board:", ". .", "Commands:", "wait 150"]
        board = ChessBoard()
        board.load_from_text_lines(input_data)
        board.process_commands(input_data)
        self.assertEqual(board.game_time_ms, 150)

    def test_click_outside_board_does_nothing(self):
        """בודק לחיצה מחוץ לגבולות הלוח כדי לכסות את שורות ה-if של הגבולות"""
        input_data = ["Board:", ". .", ". .", "Commands:", "click 999 999"]
        board = ChessBoard()
        board.load_from_text_lines(input_data)
        board.process_commands(input_data)
        # לא אמור להתרסק, פשוט להתעלם
        self.assertIsNone(board._selected_piece_pos)

if __name__ == "__main__":
    unittest.main()