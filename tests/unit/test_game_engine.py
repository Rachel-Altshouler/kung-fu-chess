import io
import runpy
import sys
import unittest
from unittest.mock import patch

from app import main
from engine.game_engine import GameEngine
from game_io.board_printer import BoardPrinter
from model.board import ChessBoard
from model.game_state import GameState
from realtime.motion import Motion
from texttests.script_runner import ScriptRunner


class TestGameEngine(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])
        self.engine = GameEngine(self.board)

    def test_handle_click_valid_king_move(self):
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertTrue(self.engine.is_moving())
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertEqual(self.board.get_piece_at((0, 0)), '.')
        self.assertFalse(self.engine.is_moving())
        self.assertIsNone(self.engine.get_selected_position())

    def test_handle_click_invalid_king_move(self):
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 50)
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((0, 2)))
        self.assertFalse(self.engine.is_moving())

    def test_handle_click_capture_enemy(self):
        self.board.set_grid([
            ['wR', '.', 'bR'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 50)
        self.engine.handle_wait(200)
        self.assertEqual(self.board.get_piece_at((0, 2)), 'wR')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_handle_click_valid_knight_move(self):
        self.board.set_grid([
            ['wN', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 150)
        self.engine.handle_wait(1000)
        self.assertEqual(self.board.get_piece_at((1, 2)), 'wN')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_cannot_command_while_moving(self):
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertTrue(self.engine.is_moving())

        self.engine.handle_click(250, 250)
        self.engine.handle_wait(50)
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((1, 1)))

        self.engine.handle_wait(50)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

    def test_cannot_start_new_move_while_piece_is_moving(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertTrue(self.engine.is_moving())

        self.assertFalse(self.engine.try_move((0, 0), (0, 1)))
        self.engine.handle_click(250, 250)
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_cannot_move_again_until_cooldown_expires(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.engine.handle_wait(100)
        self.assertFalse(self.engine.is_moving())
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertTrue(self.engine.is_piece_on_cooldown((1, 1)))

        self.engine.handle_click(150, 150)
        self.engine.handle_click(250, 250)
        self.assertFalse(self.engine.is_moving())
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

        self.engine.handle_wait(500)
        self.assertFalse(self.engine.is_piece_on_cooldown((1, 1)))

        self.engine.handle_click(150, 150)
        self.engine.handle_click(250, 250)
        self.assertTrue(self.engine.is_moving())
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((2, 2)), 'wK')

    def test_handle_click_white_pawn_move(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['.', 'wP', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(150, 150)
        self.engine.handle_click(150, 50)
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((0, 1)), 'wQ')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_board_shows_original_position_before_arrival(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)

        self.assertTrue(self.engine.is_moving())
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((1, 1)))
        self.assertEqual(
            BoardPrinter.get_canonical_representation(self.board),
            "wK . .\n. . .\n. . ."
        )

        self.engine.handle_wait(50)
        self.assertTrue(self.engine.is_moving())
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_board_shows_destination_after_sufficient_wait(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.engine.handle_wait(100)

        self.assertFalse(self.engine.is_moving())
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertTrue(self.board.is_empty((0, 0)))
        self.assertEqual(
            BoardPrinter.get_canonical_representation(self.board),
            ". . .\n. wK .\n. . ."
        )

    def test_try_move_blocked_while_moving(self):
        self.engine.try_move((0, 0), (1, 1))
        self.assertFalse(self.engine.try_move((0, 0), (1, 1)))

    def test_start_movement_with_position_object(self):
        from model.position import Position
        self.engine.try_move(Position(0, 0), Position(1, 1))
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

    def test_handle_wait(self):
        self.engine.handle_wait(100)
        self.engine.handle_wait(50)
        self.assertEqual(self.engine.get_clock(), 150)

    def test_apply_completed_skips_movement_removed_before_resolution(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.try_move((0, 0), (1, 1))
        movement = self.engine.get_active_movements()[0]
        self.engine._state.advance_clock(100)

        class ActiveList(list):
            def __contains__(self, item):
                if item is movement:
                    return False
                return super().__contains__(item)

        self.engine._state._active_movements = ActiveList(
            self.engine._state.get_active_movements_ref()
        )
        self.engine._apply_completed_movements()
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wK')

    def test_game_state_clock_and_movements(self):
        board = ChessBoard()
        board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        state = GameState(board)
        self.assertEqual(state.get_clock(), 0)
        state.advance_clock(100)
        self.assertEqual(state.get_clock(), 100)

        movement = Motion(1, 'wK', (0, 0), (1, 1), 0, 100, [((0, 0), 0), ((1, 1), 100)])
        self.assertEqual(state.allocate_movement_id(), 1)
        state.add_movement(movement)
        self.assertEqual(len(state.get_active_movements()), 1)
        state.remove_movement(movement)
        self.assertEqual(len(state.get_active_movements()), 0)
        self.assertFalse(state.is_game_over())
        state.set_game_over()
        self.assertTrue(state.is_game_over())

    def test_two_pieces_can_move_at_the_same_time(self):
        self.board.set_grid([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'wQ']
        ])
        self.engine.try_move((0, 0), (0, 2))
        self.engine.try_move((2, 2), (2, 0))
        self.assertEqual(len(self.engine.get_active_movements()), 2)
        self.engine.handle_wait(200)
        self.assertEqual(self.board.get_piece_at((0, 2)), 'wR')
        self.assertEqual(self.board.get_piece_at((2, 0)), 'wQ')

    def test_cannot_command_same_piece_while_it_is_moving(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertTrue(self.engine.is_piece_moving((0, 0)))

        self.engine.handle_click(50, 50)
        self.engine.handle_click(250, 50)
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')
        self.assertTrue(self.board.is_empty((0, 2)))

    def test_enemy_collision_later_arrival_captures(self):
        self.board.set_grid([
            ['wR', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])
        self.engine.try_move((0, 0), (1, 1))
        self.engine.try_move((2, 2), (1, 1))
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'bK')
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wR')

    def test_friendly_crossing_returns_later_piece_to_source(self):
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['wR', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', 'wQ', '.'],
            ['.', '.', '.', '.']
        ])
        self.engine.try_move((3, 2), (0, 2))
        self.engine.try_move((1, 0), (1, 3))
        self.engine.handle_wait(300)
        self.assertEqual(self.board.get_piece_at((1, 0)), 'wR')
        self.assertEqual(self.board.get_piece_at((0, 2)), 'wQ')

    def test_pawn_cannot_capture_forward_during_game(self):
        self.board.set_grid([
            ['.', 'bK', '.'],
            ['.', 'wP', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(150, 150)
        self.engine.handle_click(150, 50)
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wP')
        self.assertEqual(self.board.get_piece_at((0, 1)), 'bK')

    def test_board_unchanged_before_move_finishes(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_click(50, 50)
        self.engine.handle_click(150, 150)
        self.assertEqual(
            BoardPrinter.get_canonical_representation(self.board),
            "wK . .\n. . .\n. . ."
        )

    def test_script_runner_click(self):
        ScriptRunner.run(self.engine, ["click 50 50", "click 150 150", "wait 100"])
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

    def test_script_runner_wait(self):
        ScriptRunner.run(self.engine, ["wait 100", "wait 200"])
        self.assertEqual(self.engine.get_clock(), 300)

    def test_script_runner_print_board(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        with patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            ScriptRunner.run(self.engine, ["print board"])
            self.assertEqual(mock_stdout.getvalue().strip(), "wK . .\n. . .\n. . .")

    def test_print_board_before_and_after_movement(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        with patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            ScriptRunner.run(self.engine, [
                "click 50 50",
                "click 150 150",
                "print board",
                "wait 50",
                "print board",
                "wait 50",
                "print board",
            ])
            lines = mock_stdout.getvalue().strip().split("\n")
            boards = ["\n".join(lines[index:index + 3]) for index in range(0, len(lines), 3)]

        self.assertEqual(boards[0], "wK . .\n. . .\n. . .")
        self.assertEqual(boards[1], "wK . .\n. . .\n. . .")
        self.assertEqual(boards[2], ". . .\n. wK .\n. . .")

    def test_consecutive_moves_require_cooldown(self):
        self.board.set_grid([
            ['wK', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        with patch.object(sys, 'stdout', io.StringIO()):
            ScriptRunner.run(self.engine, [
                "click 50 50",
                "click 150 150",
                "wait 100",
                "wait 500",
                "click 150 150",
                "click 250 250",
                "wait 100",
            ])
        self.assertEqual(self.board.get_piece_at((2, 2)), 'wK')

    def test_script_runner_empty_line(self):
        ScriptRunner.run(self.engine, ["", "   "])
        self.assertIsNone(self.engine.get_selected_position())

    def test_app_valid_input(self):
        input_data = "Board:\nwK . .\n. . .\n. . .\nCommands:\nclick 50 50\nclick 150 150\nwait 100\nprint board\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()) as mock_stdout:
            main()
            self.assertIn(". wK .", mock_stdout.getvalue())
            self.assertNotIn("wK . .", mock_stdout.getvalue().split("print board")[-1])

    def test_app_invalid_board(self):
        input_data = "Board:\nwK xZ .\nCommands:\nclick 0 0\n"
        with patch('sys.stdin', io.StringIO(input_data)):
            main()

    def test_app_as_script(self):
        input_data = "Board:\nwK .\n. .\nCommands:\n"
        with patch('sys.stdin', io.StringIO(input_data)), \
             patch.object(sys, 'stdout', io.StringIO()):
            runpy.run_module('app', run_name='__main__')

    def test_cannot_capture_king(self):
        self.board.set_grid([
            ['wR', '.', 'bK'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertFalse(self.engine.try_move((0, 0), (0, 2)))
        self.assertEqual(self.board.get_piece_at((0, 2)), 'bK')
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wR')
        self.assertFalse(self.engine.is_game_over())

    def test_check_threat_ends_game_in_engine(self):
        self.board.set_grid([
            ['wR', '.', 'bK'],
            ['.', '.', '.'],
            ['wK', '.', '.']
        ])
        self.engine.handle_wait(0)
        self.assertTrue(self.engine.is_game_over())
        self.assertEqual(self.engine.get_winner(), 'w')

    def test_checkmate_ends_game_before_king_can_be_captured(self):
        self.board.set_grid([
            ['.', 'wR', 'bK'],
            ['wK', 'wR', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_wait(0)
        self.assertTrue(self.engine.is_game_over())
        self.assertEqual(self.engine.get_winner(), 'w')
        self.assertFalse(self.engine.is_stalemate())
        self.assertEqual(self.board.get_piece_at((0, 2)), 'bK')
        self.assertFalse(self.engine.try_move((0, 1), (0, 2)))

    def test_stalemate_ends_game(self):
        grid = [['.' for _ in range(8)] for _ in range(8)]
        grid[0][2] = 'bK'
        grid[2][1] = 'wQ'
        grid[2][2] = 'wK'
        self.board.set_grid(grid)
        self.engine.handle_wait(0)
        self.assertTrue(self.engine.is_game_over())
        self.assertTrue(self.engine.is_stalemate())
        self.assertIsNone(self.engine.get_winner())

    def test_late_move_commands_ignored_after_game_over(self):
        self.board.set_grid([
            ['.', 'wR', 'bK'],
            ['wK', 'wR', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_wait(0)
        self.assertTrue(self.engine.is_game_over())

        self.engine.handle_click(50, 250)
        self.engine.handle_click(150, 250)
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((1, 0)), 'wK')
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wR')

        self.assertFalse(self.engine.try_move((1, 0), (2, 0)))

    def test_white_pawn_promotes_to_queen_on_last_row(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['wP', '.', '.'],
            ['.', '.', '.'],
        ])
        self.engine.try_move((1, 0), (0, 0))
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wQ')

    def test_black_pawn_promotes_to_queen_on_last_row(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['.', '.', '.'],
            ['.', 'bP', '.'],
            ['.', '.', '.'],
        ])
        self.engine.try_move((2, 1), (3, 1))
        self.engine.handle_wait(100)
        self.assertEqual(self.board.get_piece_at((3, 1)), 'bQ')

    def test_pawn_two_square_move_through_engine(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['.', '.', '.'],
            ['.', 'wP', '.'],
            ['.', '.', '.'],
        ])
        self.engine.try_move((2, 1), (0, 1))
        self.engine.handle_wait(200)
        self.assertEqual(self.board.get_piece_at((0, 1)), 'wQ')
        self.assertTrue(self.board.is_empty((2, 1)))

    def test_knight_jump_captures_enemy_arriving_during_flight(self):
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        self.engine.try_move((1, 1), (2, 3))
        self.engine.try_move((0, 1), (2, 1))
        self.engine.handle_wait(100)
        self.assertTrue(self.board.is_empty((0, 1)))
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wN')
        self.engine.handle_wait(900)
        self.assertEqual(self.board.get_piece_at((2, 3)), 'wN')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_knight_stays_at_source_cell_during_jump(self):
        self.board.set_grid([
            ['wN', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.try_move((0, 0), (1, 2))
        self.assertTrue(self.engine.is_piece_moving((0, 0)))
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wN')
        self.assertTrue(self.board.is_empty((1, 2)))

        self.engine.handle_wait(500)
        self.assertTrue(self.engine.is_piece_moving((0, 0)))
        self.assertEqual(self.board.get_piece_at((0, 0)), 'wN')
        self.assertTrue(self.board.is_empty((1, 2)))

        self.engine.handle_wait(500)
        self.assertFalse(self.engine.is_piece_moving((0, 0)))
        self.assertEqual(self.board.get_piece_at((1, 2)), 'wN')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_knight_lands_normally_when_no_enemy_arrives_during_jump(self):
        self.board.set_grid([
            ['wN', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.engine.try_move((0, 0), (1, 2))
        self.engine.handle_wait(1000)
        self.assertEqual(self.board.get_piece_at((1, 2)), 'wN')
        self.assertTrue(self.board.is_empty((0, 0)))

    def test_captured_piece_cannot_jump(self):
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        self.engine.try_move((1, 1), (2, 3))
        self.engine.try_move((0, 1), (2, 1))
        self.engine.handle_wait(100)
        self.assertFalse(self.engine.try_move((0, 1), (1, 1)))

    def test_knight_jump_cannot_capture_king(self):
        self.board.set_grid([
            ['bK', '.', '.', '.'],
            ['.', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        self.engine.try_move((1, 1), (2, 3))
        self.engine.try_move((0, 0), (1, 1))
        self.engine.handle_wait(100)
        self.assertFalse(self.engine.is_game_over())
        self.assertEqual(self.board.get_piece_at((0, 0)), '.')
        self.assertEqual(self.board.get_piece_at((1, 1)), 'bK')

    def test_jump_command_lands_same_square(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['.', 'wK', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_jump(150, 150)
        self.engine.handle_wait(1000)
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wK')

    def test_jump_command_captures_arriving_enemy(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['wR', 'bR', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_jump(50, 150)
        self.engine.handle_click(150, 150)
        self.engine.handle_click(50, 150)
        self.engine.handle_wait(1000)
        self.assertEqual(self.board.get_piece_at((1, 0)), 'wR')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_jump_on_friendly_cell_captures_arriving_enemy(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['wR', 'bR', '.'],
            ['.', '.', '.']
        ])
        self.engine.handle_jump(50, 150)
        self.engine.handle_click(150, 150)
        self.engine.handle_click(50, 150)
        self.engine.handle_wait(1000)
        self.assertEqual(self.board.get_piece_at((1, 0)), 'wR')
        self.assertTrue(self.board.is_empty((1, 1)))

    def test_jump_on_clicked_piece(self):
        self.board.set_grid([
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', 'wP', '.', '.', '.', '.'],
            ['.', '.', 'bP', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
        ])
        self.engine.handle_jump(250, 550)
        active = self.engine.get_active_movements()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].piece_token, 'bP')
        self.assertEqual(active[0].source, (5, 2))

    def test_jump_on_black_does_not_move_adjacent_white(self):
        self.board.set_grid([
            ['.', '.', '.'],
            ['wP', 'bP', '.'],
            ['.', '.', '.'],
        ])
        self.engine.handle_jump(150, 150)
        active = self.engine.get_active_movements()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].piece_token, 'bP')
        self.assertEqual(active[0].source, (1, 1))
