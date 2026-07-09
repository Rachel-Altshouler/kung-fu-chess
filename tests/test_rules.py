import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rules import RuleEngine
from constants import MoveResult

class TestChessRules(unittest.TestCase):

    def setUp(self):
        self.engine = RuleEngine()

    def test_rook_blocked_path(self):
        """בדיקה שצריח נחסם כשיש כלי אחר במסלול שלו"""
        grid = [
            ["wR", ".", "."],
            ["wP", ".", "."],
            [".",  ".", "."]
        ]
        result = self.engine.validate_move(0, 0, 2, 0, grid)
        self.assertEqual(result, MoveResult.ILLEGAL_PIECE_MOVE)

    def test_knight_can_jump(self):
        """בדיקה שפרש מדלג מעל כלים חוסמים בהצלחה"""
        grid = [
            ["wN", ".", "."],
            ["bP", "bP", "."],
            [".",  ".", "."]
        ]
        result = self.engine.validate_move(0, 0, 2, 1, grid)
        self.assertEqual(result, MoveResult.OK)

    def test_friendly_destination_is_blocked(self):
        """בדיקה שלא ניתן לנחות על משבצת של כלי מאותו הצבע"""
        grid = [["wR", ".", "wP"]]
        result = self.engine.validate_move(0, 0, 0, 2, grid)
        self.assertEqual(result, MoveResult.FRIENDLY_DESTINATION)

    def test_bishop_move(self):
        # בדיקה שהרץ נע באלכסון חוקי
        from rules import Bishop
        bishop = Bishop()
        # נניח לוח ריק בגודל 8 על 8
        grid = [["." for _ in range(8)] for _ in range(8)]

        # תנועה אלכסונית חוקית מרחוק
        self.assertTrue(bishop.is_move_allowed(grid, 2, 2, 5, 5))
        # תנועה לא אלכסונית (לא חוקית לרץ)
        self.assertFalse(bishop.is_move_allowed(grid, 2, 2, 2, 5))

    def test_bishop_move(self):
        # מייבאים את המחלקה המדויקת מהקוד שלכן
        from rules import BishopRule
        bishop = BishopRule()
        # יוצרים לוח ריק (8 על 8) שמלא בנקודות לפי הקבועים שלכן
        from constants import BoardConstants
        grid = [[BoardConstants.EMPTY_CELL for _ in range(8)] for _ in range(8)]

        # 1. תנועה אלכסונית חוקית (אמור להחזיר True)
        self.assertTrue(bishop.is_move_allowed(2, 2, 5, 5, grid))
        # 2. תנועה לא אלכסונית - למשל ישר ימינה (אמור להחזיר False)
        self.assertFalse(bishop.is_move_allowed(2, 2, 2, 5, grid))

    def test_queen_move(self):
        # מייבאים את מחלקת המלכה המדויקת מהקוד שלכן
        from rules import QueenRule
        queen = QueenRule()
        from constants import BoardConstants
        grid = [[BoardConstants.EMPTY_CELL for _ in range(8)] for _ in range(8)]

        # 1. תנועה ישרה חוקית כמו צריח (אמור להחזיר True)
        self.assertTrue(queen.is_move_allowed(0, 0, 0, 5, grid))
        # 2. תנועה אלכסונית חוקית כמו רץ (אמור להחזיר True)
        self.assertTrue(queen.is_move_allowed(0, 0, 3, 3, grid))
        # 3. תנועה לא חוקית (אמור להחזיר False)
        self.assertFalse(queen.is_move_allowed(0, 0, 1, 2, grid))
if __name__ == "__main__":
    unittest.main()