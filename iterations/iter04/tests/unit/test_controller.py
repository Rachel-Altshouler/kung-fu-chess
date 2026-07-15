import unittest
from engine.game_engine import GameEngine
from input.controller import Controller
from model.board import ChessBoard


class TestController(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])
        self.engine = GameEngine(self.board)
        self.controller = self.engine._controller

    def test_select_piece_on_first_click(self):
        self.controller.handle_click(self.engine, 50, 50)
        self.assertEqual(self.controller.get_selected_position().as_tuple(), (0, 0))

    def test_ignore_empty_cell_without_selection(self):
        self.controller.handle_click(self.engine, 250, 50)
        self.assertIsNone(self.controller.get_selected_position())

    def test_reselect_friendly_piece(self):
        self.controller.handle_click(self.engine, 50, 50)
        self.controller.handle_click(self.engine, 150, 50)
        self.assertEqual(self.controller.get_selected_position().as_tuple(), (0, 1))

    def test_click_outside_board(self):
        self.controller.handle_click(self.engine, 500, 500)
        self.assertIsNone(self.controller.get_selected_position())
