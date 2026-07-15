import unittest
from game_io.board_parser import BoardParser


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

        lines = ["Board:", "wK .", "Commands:", "click 0 0"]
        self.assertIsNotNone(BoardParser.parse_from_lines(lines))

        lines = ["Board:", "wK xZ"]
        self.assertIsNone(BoardParser.parse_from_lines(lines))

        lines = ["Board:", "wK .", "wK"]
        self.assertIsNone(BoardParser.parse_from_lines(lines))
