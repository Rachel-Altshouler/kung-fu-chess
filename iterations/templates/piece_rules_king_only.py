from model.constants import BoardConstants


class PieceRules:
    @staticmethod
    def is_path_blocked(grid, source_position, destination_position):
        source_row, source_col = source_position
        destination_row, destination_col = destination_position

        row_step = 0 if destination_row == source_row else (1 if destination_row > source_row else -1)
        col_step = 0 if destination_col == source_col else (1 if destination_col > source_col else -1)

        current_row = source_row + row_step
        current_col = source_col + col_step
        while (current_row, current_col) != (destination_row, destination_col):
            if grid[current_row][current_col] != BoardConstants.EMPTY_CELL:
                return True
            current_row += row_step
            current_col += col_step
        return False

    @staticmethod
    def is_king_move(source_position, destination_position) -> bool:
        row_delta = abs(destination_position[0] - source_position[0])
        col_delta = abs(destination_position[1] - source_position[1])
        return row_delta <= 1 and col_delta <= 1

    @staticmethod
    def is_piece_move_valid(grid, piece_type, source_position, destination_position, color) -> bool:
        if piece_type == 'K':
            return PieceRules.is_king_move(source_position, destination_position)
        return False
