import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from board import ChessBoard

class TestChessIntegration(unittest.TestCase):

    def test_full_move_and_capture_sequence(self):
        """בדיקת שילוב: לחיצה, תנועה, אכילת אויב והדפסה"""
        input_data = [
            "Board:",
            "wR . bP",
            ". . .",
            "Commands:",
            "click 50 50",    # בחירת צריח לבן
            "click 250 50",   # אכילת פיון שחור ביעד
            "print board"
        ]
        board = ChessBoard()
        board.load_from_text_lines(input_data)
        board.process_commands(input_data)
        self.assertEqual(board.get_canonical_representation(), ". . wR\n. . .")

if __name__ == "__main__":
    unittest.main()