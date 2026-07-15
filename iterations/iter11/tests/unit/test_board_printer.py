import unittest
from model.board import ChessBoard
from game_io.board_printer import BoardPrinter
from view.renderer import Renderer


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
        actual_output = BoardPrinter.get_canonical_representation(self.board)
        self.assertEqual(actual_output, expected_output)

    def test_empty_board(self):
        self.board.set_grid([['.', '.'], ['.', '.']])
        expected_output = ". .\n. ."
        self.assertEqual(BoardPrinter.get_canonical_representation(self.board), expected_output)

    def test_renderer_uses_board_printer(self):
        self.board.set_grid([
            ['wK', '.'],
            ['.', '.']
        ])
        self.assertEqual(Renderer.render_text(self.board), "wK .\n. .")

    def test_image_view_not_available_in_text_mode(self):
        from view.image_view import ImageView
        view = ImageView()
        self.assertFalse(view.is_enabled())
        self.board.set_grid([['.', '.'], ['.', '.']])
        with self.assertRaises(NotImplementedError):
            view.render(self.board)
