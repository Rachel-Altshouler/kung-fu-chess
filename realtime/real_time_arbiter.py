from model.constants import BoardConstants, PieceTypes
from model.piece import Piece
from realtime.motion import Motion


class RealTimeArbiter:
    @staticmethod
    def apply_jump_captures(active_movements, board, clock):
        captured = []
        for jumper in active_movements:
            if not Motion.is_jump_movement(jumper):
                continue

            jumper_piece = Piece.from_token(jumper.piece_token)
            jump_start = jumper.start_time
            jump_end = jumper.finish_time

            for other in active_movements:
                if other is jumper or other in captured:
                    continue

                other_piece = Piece.from_token(other.piece_token)
                if jumper_piece.is_same_color(other_piece):
                    continue
                if other_piece.piece_type == PieceTypes.KING:
                    continue

                arrival_time = RealTimeArbiter._find_arrival_during_jump(
                    other.path, jumper.source, jump_start, jump_end
                )
                if arrival_time is None or arrival_time > clock:
                    continue

                board.set_piece_at(other.source, BoardConstants.EMPTY_CELL)
                captured.append(other)
                jumper.airborne_capture_occurred = True

        return captured

    @staticmethod
    def find_jump_capturer(captured_movement, active_movements):
        captured_piece = Piece.from_token(captured_movement.piece_token)
        if captured_piece is None:
            return None

        for jumper in active_movements:
            if not Motion.is_jump_movement(jumper):
                continue

            jumper_piece = Piece.from_token(jumper.piece_token)
            if jumper_piece is None:
                continue
            if jumper_piece.is_same_color(captured_piece):
                continue

            arrival_time = RealTimeArbiter._find_arrival_during_jump(
                captured_movement.path,
                jumper.source,
                jumper.start_time,
                jumper.finish_time,
            )
            if arrival_time is None:
                continue
            if not getattr(jumper, "airborne_capture_occurred", False):
                continue
            return jumper

        return None

    @staticmethod
    def _find_arrival_during_jump(path, cell, jump_start, jump_end):
        for path_cell, path_time in path:
            if path_cell == cell and jump_start <= path_time < jump_end:
                return path_time
        return None

    @staticmethod
    def resolve_destination(movement, active_movements, board):
        piece = Piece.from_token(movement.piece_token)
        destination = movement.destination

        if movement.is_jump and movement.airborne_capture_occurred:
            return movement.source

        for other in active_movements:
            if other is movement or other.source == movement.source:
                continue

            other_piece = Piece.from_token(other.piece_token)
            conflict = RealTimeArbiter._find_path_conflict(movement.path, other.path)
            if conflict is None:
                route_conflict = RealTimeArbiter._find_common_route_conflict(
                    movement.path, other.path
                )
                if route_conflict is not None and not piece.is_same_color(other_piece):
                    if movement.movement_id > other.movement_id:
                        return movement.source
                continue

            if piece.is_same_color(other_piece):
                if movement.movement_id > other.movement_id:
                    return movement.source
                continue
            else:
                if movement.movement_id > other.movement_id:
                    destination = conflict[0]
                elif movement.movement_id < other.movement_id:
                    destination = RealTimeArbiter._cell_before_on_path(
                        movement.path, conflict[0]
                    )

        if not board.is_within_bounds(*destination):
            return movement.source

        destination_token = board.get_piece_at(destination)
        destination_piece = Piece.from_token(destination_token)
        if destination_piece is not None and piece.is_same_color(destination_piece):
            return movement.source

        return destination

    @staticmethod
    def _find_path_conflict(first_path, second_path):
        second_lookup = {cell: time for cell, time in second_path}
        for cell, time in first_path:
            if cell in second_lookup and second_lookup[cell] == time:
                return cell, time
        return None

    @staticmethod
    def _find_common_route_conflict(first_path, second_path):
        second_by_time = {time: cell for cell, time in second_path}
        for cell, time in first_path:
            other_cell = second_by_time.get(time)
            if other_cell is None or other_cell == cell:
                continue
            if cell[1] == other_cell[1] or cell[0] == other_cell[0]:
                return cell, time
        return None

    @staticmethod
    def _cell_before_on_path(path, conflict_cell):
        previous_cell = path[0][0]
        for cell, _time in path:
            if cell == conflict_cell:
                return previous_cell
            previous_cell = cell
        return path[-1][0]
