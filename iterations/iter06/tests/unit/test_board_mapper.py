import unittest
from input.board_mapper import BoardMapper
from model.board import ChessBoard


class TestBoardMapper(unittest.TestCase):
    def setUp(self):
        self.board = ChessBoard()
        self.board.set_grid([
            ['wK', 'wN', '.'],
            ['.', '.', '.'],
            ['.', '.', 'bK']
        ])

    def test_pixel_to_position_empty_board(self):
        board = ChessBoard()
        self.assertIsNone(BoardMapper.pixel_to_position(board, 0, 0))

    def test_pixel_to_position_valid(self):
        position = BoardMapper.pixel_to_position(self.board, 50, 50)
        self.assertEqual(position.as_tuple(), (0, 0))

    def test_pixel_to_position_out_of_bounds(self):
        self.assertIsNone(BoardMapper.pixel_to_position(self.board, 500, 500))
