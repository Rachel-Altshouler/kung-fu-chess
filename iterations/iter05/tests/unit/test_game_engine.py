import io
import runpy
import sys
import unittest
from unittest.mock import patch
from engine.game_engine import GameEngine
from main import main
from model.board import ChessBoard
from texttests.script_runner import ScriptRunner

class TestGameEngine(unittest.TestCase):

    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([['wK', 'wN', '.'], ['.', '.', '.'], ['.', '.', 'bK']])
        self.engine = GameEngine(self.board)

    def test_handle_click_valid_king_move(self):
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertEqual(self.board.get_piece_at((0, 0)), '.')
        self.assertFalse(self.engine.is_moving())

    def test_handle_click_invalid_king_move(self):
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 50)
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((0, 2)))

    def test_handle_click_capture_enemy(self):
        self.board.set_grid([['wR', '.', 'bK'], ['.', '.', '.'], ['.', '.', '.']])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 50)
        self.assertEqual(self.board.get_piece_at((0, 2)), 'wR')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_handle_click_valid_knight_move(self):
        self.board.set_grid([['wN', '.', '.'], ['.', '.', '.'], ['.', '.', '.']])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 150)
        self.assertEqual(self.board.get_piece_at((1, 2)), 'wN')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_pawn_cannot_capture_forward_during_game(self):
        self.board.set_grid([['.', 'bK', '.'], ['.', 'wP', '.'], ['.', '.', '.']])
        self.engine.handle_click(150, 150)
        self.engine.handle_click(150, 50)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wP')
        self.assertEqual(self.board.get_piece_at((0, 1)), 'bK')

    def test_handle_wait(self):
        self.engine.handle_wait(100)
        self.engine.handle_wait(50)
        self.assertEqual(self.engine.get_clock(), 150)

    def test_script_runner_click(self):
        ScriptRunner.run(self.engine, ['click 50 50', 'click 150 150'])
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

    def test_script_runner_wait(self):
        ScriptRunner.run(self.engine, ['wait 100', 'wait 200'])
        self.assertEqual(self.engine.get_clock(), 300)

    def test_script_runner_print_board(self):
        with patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            ScriptRunner.run(self.engine, ['print board'])
            self.assertEqual(mock_stdout.getvalue().strip(), 'wK wN .\n. . .\n. . bK')

    def test_script_runner_empty_line(self):
        ScriptRunner.run(self.engine, ['', '   '])
        self.assertIsNone(self.engine.get_selected_position())

    def test_app_valid_input(self):
        input_data = 'Board:\nwK . .\n. . .\n. . .\nCommands:\nclick 50 50\nclick 150 150\nprint board\n'
        with patch('sys.stdin', io.StringIO(input_data)), patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            main()
            self.assertIn('. wK .', mock_stdout.getvalue())

    def test_app_invalid_board(self):
        input_data = 'Board:\nwK xZ .\nCommands:\nclick 0 0\n'
        with patch('sys.stdin', io.StringIO(input_data)):
            main()

    def test_app_as_script(self):
        input_data = 'Board:\nwK .\n. .\nCommands:\n'
        with patch('sys.stdin', io.StringIO(input_data)), patch.object(sys, 'stdout', io.StringIO()):
            runpy.run_module('main', run_name='__main__')
