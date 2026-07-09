import unittest
import sys
import os

# מבטיח שפייתון רואה את התיקייה הראשית קודם כל
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from validators import BoardValidator

class TestBoardValidators(unittest.TestCase):

    def test_valid_tokens(self):
        """ודא שכל הכלים החוקיים עוברים בהצלחה"""
        self.assertTrue(BoardValidator.is_token_valid("."))
        self.assertTrue(BoardValidator.is_token_valid("wR"))
        self.assertTrue(BoardValidator.is_token_valid("bP"))
        self.assertTrue(BoardValidator.is_token_valid("wN"))

    def test_invalid_tokens(self):
        """ודא שכל כלי לא חוקי נפסל מיד"""
        self.assertFalse(BoardValidator.is_token_valid("wX"))  # כלי x לא קיים
        self.assertFalse(BoardValidator.is_token_valid("zR"))  # צבע z לא קיים
        self.assertFalse(BoardValidator.is_token_valid("wRR")) # אורך לא תקין
        self.assertFalse(BoardValidator.is_token_valid(""))    # ריק

    def test_row_width_mismatch(self):
        """ודא שלוח עם שורות לא שוות נפסל"""
        invalid_grid = [[".", "wR"], ["."]]
        self.assertFalse(BoardValidator.validate_row_widths(invalid_grid))

    def test_row_width_match(self):
        """ודא שלוח תקין עובר"""
        valid_grid = [[".", "wR"], [".", "."]]
        self.assertTrue(BoardValidator.validate_row_widths(valid_grid))

if __name__ == "__main__":
    unittest.main()