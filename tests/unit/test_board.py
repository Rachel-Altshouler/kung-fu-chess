import unittest
from model.board import ChessBoard


class TestChessBoard(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])

    def test_pixel_to_grid_empty_board(self):
        board = ChessBoard()
        self.assertIsNone(board.pixel_to_grid(0, 0))

    def test_pixel_to_grid_out_of_bounds(self):
        self.assertIsNone(self.board.pixel_to_grid(500, 500))

    def test_handle_click_outside_board(self):
        self.board.handle_click(500, 500)
        self.assertIsNone(self.board._selected_piece)

    def test_handle_click_empty_cell_no_selection(self):
        self.board.handle_click(250, 50)
        self.assertIsNone(self.board._selected_piece)

    def test_handle_click_select_friendly_piece(self):
        self.board.handle_click(50, 50)
        self.board.handle_click(150, 50)
        self.assertEqual(self.board._selected_piece, (0, 1))

    def test_is_friendly(self):
        self.assertTrue(self.board.is_friendly((0, 0), (0, 1)))
        self.assertFalse(self.board.is_friendly((0, 0), (2, 2)))

    def test_handle_wait(self):
        self.board.handle_wait(100)
        self.board.handle_wait(50)
        self.assertEqual(self.board._clock, 150)

    def test_execute_move(self):
        self.board.execute_move((0, 0), (1, 1))
        self.assertEqual(self.board.get_grid()[1][1], 'wK')
        self.assertEqual(self.board.get_grid()[0][0], '.')

    def test_handle_click_valid_king_move(self):
        self.board.handle_click(50, 50)
        self.board.handle_click(150, 150)
        self.assertEqual(self.board.get_grid()[1][1], 'wK')
        self.assertEqual(self.board.get_grid()[0][0], '.')
        self.assertIsNone(self.board._selected_piece)

    def test_handle_click_invalid_king_move(self):
        self.board.handle_click(50, 50)
        self.board.handle_click(250, 50)
        self.assertEqual(self.board.get_grid()[0][0], 'wK')
        self.assertEqual(self.board.get_grid()[0][2], '.')
        self.assertIsNone(self.board._selected_piece)

    def test_is_valid_move_king(self):
        self.assertTrue(self.board.is_valid_move((0, 0), (1, 1)))
        self.assertFalse(self.board.is_valid_move((0, 0), (0, 2)))

    def test_is_valid_move_rook(self):
        self.board.set_grid([
            ['wR', '.', '.'],
            ['wP', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertTrue(self.board.is_valid_move((0, 0), (0, 2)))
        self.assertFalse(self.board.is_valid_move((0, 0), (2, 0)))
        self.assertFalse(self.board.is_valid_move((0, 0), (1, 1)))

    def test_is_valid_move_bishop(self):
        self.board.set_grid([
            ['wB', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertTrue(self.board.is_valid_move((0, 0), (2, 2)))

        self.board.set_grid([
            ['wB', '.', '.'],
            ['.', 'wP', '.'],
            ['.', '.', '.']
        ])
        self.assertFalse(self.board.is_valid_move((0, 0), (2, 2)))
        self.assertFalse(self.board.is_valid_move((0, 0), (0, 2)))

    def test_is_valid_move_queen(self):
        self.board.set_grid([
            ['wQ', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertTrue(self.board.is_valid_move((0, 0), (0, 2)))
        self.assertTrue(self.board.is_valid_move((0, 0), (2, 2)))
        self.assertFalse(self.board.is_valid_move((0, 0), (1, 2)))

    def test_is_valid_move_knight(self):
        self.board.set_grid([
            ['wN', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertTrue(self.board.is_valid_move((0, 0), (1, 2)))
        self.assertTrue(self.board.is_valid_move((0, 0), (2, 1)))
        self.assertFalse(self.board.is_valid_move((0, 0), (2, 2)))

    def test_is_valid_move_pawn_returns_false(self):
        self.board.set_grid([
            ['wP', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertFalse(self.board.is_valid_move((0, 0), (1, 0)))

    def test_is_path_blocked(self):
        self.board.set_grid([
            ['wR', 'wP', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.assertTrue(self.board.is_path_blocked((0, 0), (0, 2)))
        self.assertFalse(self.board.is_path_blocked((0, 0), (0, 1)))

    def test_handle_click_valid_knight_move(self):
        self.board.set_grid([
            ['wN', '.', '.'],
            ['.', '.', '.'],
            ['.', '.', '.']
        ])
        self.board.handle_click(50, 50)
        self.board.handle_click(250, 150)
        self.assertEqual(self.board.get_grid()[1][2], 'wN')
        self.assertEqual(self.board.get_grid()[0][0], '.')


if __name__ == '__main__':
    unittest.main()
