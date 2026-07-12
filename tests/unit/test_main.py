import io
import runpy
import sys
import unittest
from unittest.mock import patch

from main import main, process_commands
from model.board import ChessBoard


class TestMain(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])

    def test_process_commands_click(self):
        process_commands(self.board, ["click 50 50", "click 150 150"])
        self.assertEqual(self.board.get_grid()[1][1], 'wK')

    def test_process_commands_wait(self):
        process_commands(self.board, ["wait 100", "wait 200"])
        self.assertEqual(self.board._clock, 300)

    def test_process_commands_print_board(self):
        with patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            process_commands(self.board, ["print board"])
            self.assertEqual(mock_stdout.getvalue().strip(), "wK . .\n. . .\n. . .")

    def test_process_commands_empty_line(self):
        process_commands(self.board, ["", "   "])
        self.assertIsNone(self.board._selected_piece)

    def test_main_valid_input(self):
        input_data = "Board:\nwK . .\n. . .\n. . .\nCommands:\nclick 50 50\nclick 150 150\nwait 100\nprint board\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            main()
            self.assertIn("wK", mock_stdout.getvalue())

    def test_main_invalid_board(self):
        input_data = "Board:\nwK xZ .\nCommands:\nclick 0 0\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            main()

    def test_main_as_script(self):
        input_data = "Board:\nwK .\n. .\nCommands:\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()):
            runpy.run_module('main', run_name='__main__')


if __name__ == '__main__':
    unittest.main()
