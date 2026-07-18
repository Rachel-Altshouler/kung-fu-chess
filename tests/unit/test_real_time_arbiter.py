import unittest
from model.board import ChessBoard
from realtime.motion import Motion
from realtime.real_time_arbiter import RealTimeArbiter


class TestRealTimeArbiter(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])

    def _make_movement(self, movement_id, token, source, destination, start_time, is_jump=False):
        piece_type = token[1]
        path = Motion.build_path(piece_type, source, destination, start_time, is_jump=is_jump)
        return Motion(
            movement_id,
            token,
            source,
            destination,
            start_time,
            path[-1][1],
            path,
            is_jump=is_jump or piece_type == 'N',
        )

    def test_friendly_path_conflict_returns_later_piece_to_source(self):
        first = self._make_movement(1, 'wQ', (3, 2), (0, 2), 0)
        second = self._make_movement(2, 'wR', (1, 0), (1, 3), 0)
        destination = RealTimeArbiter.resolve_destination(second, [first, second], self.board)
        self.assertEqual(destination, (1, 0))

    def test_enemy_collision_later_piece_wins_square(self):
        first = self._make_movement(1, 'wR', (0, 0), (1, 1), 0)
        second = self._make_movement(2, 'bK', (2, 2), (1, 1), 0)
        destination = RealTimeArbiter.resolve_destination(second, [first, second], self.board)
        self.assertEqual(destination, (1, 1))

    def test_cannot_land_on_friendly_square(self):
        self.board.set_grid([
            ['wR', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        movement = self._make_movement(1, 'wR', (0, 0), (0, 1), 0)
        destination = RealTimeArbiter.resolve_destination(movement, [movement], self.board)
        self.assertEqual(destination, (0, 0))

    def test_enemy_collision_earlier_piece_stops_short(self):
        first = self._make_movement(1, 'wR', (0, 0), (1, 1), 0)
        second = self._make_movement(2, 'bK', (2, 2), (1, 1), 0)
        destination = RealTimeArbiter.resolve_destination(first, [first, second], self.board)
        self.assertEqual(destination, (0, 0))

    def test_resolve_destination_out_of_bounds_returns_source(self):
        movement = self._make_movement(1, 'wR', (0, 0), (9, 9), 0)
        destination = RealTimeArbiter.resolve_destination(movement, [movement], self.board)
        self.assertEqual(destination, (0, 0))

    def test_skips_other_movements_with_same_source(self):
        first = self._make_movement(1, 'wR', (0, 0), (0, 2), 0)
        duplicate_source = self._make_movement(2, 'wR', (0, 0), (0, 1), 0)
        destination = RealTimeArbiter.resolve_destination(first, [first, duplicate_source], self.board)
        self.assertEqual(destination, (0, 2))

    def test_cell_before_on_path_returns_last_cell_when_conflict_missing(self):
        path = [((0, 0), 0), ((0, 1), 100)]
        cell = RealTimeArbiter._cell_before_on_path(path, (5, 5))
        self.assertEqual(cell, (0, 1))

    def test_build_path_for_knight(self):
        path = Motion.build_path('N', (0, 0), (1, 2), 0)
        self.assertEqual(path[-1][0], (1, 2))

    def test_rook_timed_path(self):
        path = Motion.build_timed_path((1, 0), (1, 3), 0)
        self.assertEqual(path[0], ((1, 0), 0))
        self.assertEqual(path[-1], ((1, 3), 300))

    def test_knight_timed_path(self):
        path = Motion.build_knight_path((0, 0), (1, 2), 0)
        self.assertEqual(path[0], ((0, 0), 0))
        self.assertEqual(path[-1], ((1, 2), 1000))

    def test_jump_capture_removes_arriving_enemy(self):
        first = self._make_movement(1, 'wN', (1, 1), (2, 3), 0)
        second = self._make_movement(2, 'bR', (0, 1), (2, 1), 0)
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        captured = RealTimeArbiter.apply_jump_captures(
            [first, second], self.board, 100
        )
        self.assertEqual(captured, [second])
        self.assertTrue(first.airborne_capture_occurred)
        self.assertTrue(self.board.is_empty((0, 1)))
        self.assertEqual(self.board.get_piece_at((1, 1)), 'wN')

    def test_no_jump_capture_when_enemy_arrives_after_jump(self):
        knight = self._make_movement(1, 'wN', (1, 1), (2, 3), 0)
        rook_path = Motion.build_timed_path((0, 1), (2, 1), 1000)
        rook = Motion(
            2, 'bR', (0, 1), (2, 1), 1000, rook_path[-1][1], rook_path
        )
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        captured = RealTimeArbiter.apply_jump_captures(
            [knight, rook], self.board, 1100
        )
        self.assertEqual(captured, [])

    def test_jump_capture_skips_friendly_piece(self):
        knight = self._make_movement(1, 'wN', (1, 1), (2, 3), 0)
        rook = self._make_movement(2, 'wR', (0, 1), (2, 1), 0)
        captured = RealTimeArbiter.apply_jump_captures([knight, rook], self.board, 100)
        self.assertEqual(captured, [])

    def test_jump_capture_waits_until_arrival_time(self):
        knight = self._make_movement(1, 'wN', (1, 1), (2, 3), 0)
        rook = self._make_movement(2, 'bR', (0, 1), (2, 1), 0)
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', '.', '.'],
            ['.', '.', '.', '.'],
        ])
        captured = RealTimeArbiter.apply_jump_captures([knight, rook], self.board, 50)
        self.assertEqual(captured, [])

    def test_jump_capture_skips_already_captured_enemy(self):
        knight_one = self._make_movement(1, 'wN', (1, 1), (2, 3), 0)
        knight_two = self._make_movement(3, 'wN', (2, 2), (0, 3), 0)
        rook = self._make_movement(2, 'bR', (0, 1), (2, 1), 0)
        self.board.set_grid([
            ['.', '.', '.', '.'],
            ['bR', 'wN', '.', '.'],
            ['.', '.', 'wN', '.'],
            ['.', '.', '.', '.'],
        ])
        captured = RealTimeArbiter.apply_jump_captures(
            [knight_one, knight_two, rook], self.board, 100
        )
        self.assertEqual(captured, [rook])
