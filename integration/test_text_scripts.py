import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from app import main

SCRIPTS_DIR = Path(__file__).parent / "scripts"

EXPECTED_BOARDS = {
    "01_board_parsing.kfc": "wK . .\n. . .\n. . .",
    "02_click_to_move.kfc": ". . .\n. wK .\n. . .",
    "03_rook_moves.kfc": ". . . wR\n. . . .\n. . . .",
    "04_invalid_moves.kfc": "wK . .\n. . .\n. . .",
    "05_capture.kfc": ". . wR\n. . .\n. . .",
    "06_game_over.kfc": ". wR bK\nwK wR .\n. . .",
}


def run_kfc_script(script_name: str) -> str:
    script_path = SCRIPTS_DIR / script_name
    with open(script_path, encoding="utf-8") as script_file:
        input_data = script_file.read()
    with patch("sys.stdin", io.StringIO(input_data)), \
         patch.object(sys, "stdout", io.StringIO()) as mock_stdout:
        main()
        return mock_stdout.getvalue().strip()


class TestTextScripts(unittest.TestCase):
    def test_01_board_parsing(self):
        output = run_kfc_script("01_board_parsing.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["01_board_parsing.kfc"])

    def test_02_click_to_move(self):
        output = run_kfc_script("02_click_to_move.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["02_click_to_move.kfc"])

    def test_03_rook_moves(self):
        output = run_kfc_script("03_rook_moves.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["03_rook_moves.kfc"])

    def test_04_invalid_moves(self):
        output = run_kfc_script("04_invalid_moves.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["04_invalid_moves.kfc"])

    def test_05_capture(self):
        output = run_kfc_script("05_capture.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["05_capture.kfc"])

    def test_06_game_over(self):
        output = run_kfc_script("06_game_over.kfc")
        self.assertEqual(output, EXPECTED_BOARDS["06_game_over.kfc"])

    def test_invalid_token_board(self):
        input_data = "Board:\nwK xZ .\nCommands:\nprint board\n"
        with patch("sys.stdin", io.StringIO(input_data)), \
             patch.object(sys, "stdout", io.StringIO()) as mock_stdout:
            main()
            self.assertIn("ERROR UNKNOWN_TOKEN", mock_stdout.getvalue())

    def test_row_width_mismatch(self):
        input_data = "Board:\nwK .\n. . .\nCommands:\nprint board\n"
        with patch("sys.stdin", io.StringIO(input_data)), \
             patch.object(sys, "stdout", io.StringIO()) as mock_stdout:
            main()
            self.assertIn("ERROR ROW_WIDTH_MISMATCH", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
