import io
import runpy
import sys
import unittest
from unittest.mock import patch

from game_io.board_parser import BoardParser
from main import main, parse_commands, process_commands
from model.board import ChessBoard


class TestBoardParser(unittest.TestCase):

    def test_valid_tokens(self):
        self.assertTrue(BoardParser.is_token_valid("."))
        self.assertTrue(BoardParser.is_token_valid("wK"))
        self.assertTrue(BoardParser.is_token_valid("bP"))

    def test_invalid_token(self):
        self.assertFalse(BoardParser.is_token_valid("zX"))
        self.assertFalse(BoardParser.is_token_valid("wZ"))
        self.assertFalse(BoardParser.is_token_valid("w"))

    def test_row_width_empty(self):
        self.assertTrue(BoardParser.validate_row_widths([]))

    def test_row_width_mismatch(self):
        rows = [["wP", "wP"], ["wP"]]
        self.assertFalse(BoardParser.validate_row_widths(rows))

    def test_row_width_valid(self):
        rows = [["wP", "wP"], ["wP", "wP"]]
        self.assertTrue(BoardParser.validate_row_widths(rows))

    def test_parser_edge_cases(self):
        self.assertIsNone(BoardParser.parse_from_lines([]))
        self.assertIsNone(BoardParser.parse_from_lines(["Commands:"]))

    def test_parser_full_coverage(self):
        self.assertIsNone(BoardParser.parse_from_lines(["", "Board:", ""]))

        lines = ["Board:", "wK .", "Commands:", "print board"]
        self.assertIsNotNone(BoardParser.parse_from_lines(lines))

        lines = ["Board:", "wK xZ"]
        self.assertIsNone(BoardParser.parse_from_lines(lines))

        lines = ["Board:", "wK .", "wK"]
        self.assertIsNone(BoardParser.parse_from_lines(lines))


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
        from game_io.board_printer import BoardPrinter
        self.assertEqual(BoardPrinter.get_canonical_representation(self.board), expected_output)

    def test_empty_board(self):
        self.board.set_grid([['.', '.'], ['.', '.']])
        from game_io.board_printer import BoardPrinter
        self.assertEqual(BoardPrinter.get_canonical_representation(self.board), ". .\n. .")


class TestMain(unittest.TestCase):
    def test_process_commands_print_board(self):
        board = ChessBoard()
        board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        with patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            process_commands(board, ["print board"])
            self.assertEqual(mock_stdout.getvalue().strip(), "wK . .\n. . .\n. . .")

    def test_process_commands_empty_line(self):
        board = ChessBoard()
        board.set_grid([['.', '.'], ['.', '.']])
        process_commands(board, ["", "   "])

    def test_main_valid_input(self):
        input_data = "Board:\nwK . .\n. . .\n. . .\nCommands:\nprint board\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            main()
            self.assertEqual(mock_stdout.getvalue().strip(), "wK . .\n. . .\n. . .")

    def test_main_invalid_board(self):
        input_data = "Board:\nwK xZ .\nCommands:\nprint board\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            main()
            self.assertEqual(mock_stdout.getvalue(), "")

    def test_main_as_script(self):
        input_data = "Board:\nwK .\n. .\nCommands:\nprint board\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            runpy.run_module('main', run_name='__main__')
            self.assertIn("wK", mock_stdout.getvalue())
