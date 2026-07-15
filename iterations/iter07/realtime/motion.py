from model.constants import BoardConstants


class Motion:
    def __init__(
        self,
        movement_id,
        piece_token,
        source,
        destination,
        start_time,
        finish_time,
        path,
        is_jump=False,
    ):
        self.movement_id = movement_id
        self.piece_token = piece_token
        self.source = source
        self.destination = destination
        self.start_time = start_time
        self.finish_time = finish_time
        self.path = path
        self.resolved_destination = destination
        self.is_jump = is_jump
        self.airborne_capture_occurred = False

    @staticmethod
    def build_path(piece_type, source, destination, start_time, is_jump=False):
        if is_jump or piece_type == 'N':
            return Motion.build_jump_path(source, destination, start_time)
        return Motion.build_timed_path(source, destination, start_time)

    @staticmethod
    def build_timed_path(source, destination, start_time):
        source_row, source_col = source
        destination_row, destination_col = destination
        row_step = 0 if destination_row == source_row else (1 if destination_row > source_row else -1)
        col_step = 0 if destination_col == source_col else (1 if destination_col > source_col else -1)

        path = []
        current_time = start_time
        current_row, current_col = source_row, source_col
        path.append(((current_row, current_col), current_time))

        while (current_row, current_col) != (destination_row, destination_col):
            current_row += row_step
            current_col += col_step
            current_time += BoardConstants.MS_PER_SQUARE
            path.append(((current_row, current_col), current_time))

        return path

    @staticmethod
    def build_jump_path(source, destination, start_time):
        return [
            (source, start_time),
            (destination, start_time + BoardConstants.MS_KNIGHT_JUMP),
        ]

    @staticmethod
    def build_knight_path(source, destination, start_time):
        return Motion.build_jump_path(source, destination, start_time)

    @staticmethod
    def is_jump_movement(movement):
        return movement.is_jump

    @staticmethod
    def is_knight_movement(movement):
        return movement.piece_token[1] == 'N'
