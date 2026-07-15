from input.board_mapper import BoardMapper
from rules.rule_engine import RuleEngine


class Controller:
    #יוצרת בקר ללא כלי נבחר
    def __init__(self):
        self._selected_position = None

    #מחזירה את המיקום הנבחר
    def get_selected_position(self):
        return self._selected_position

    def clear_selection(self):
        self._selected_position = None

    #מטפלת הלחיצה-בחירת כלי, החלפת בחירה, נסיון מהלך
    def handle_click(self, game_engine, x: int, y: int):
        board = game_engine.get_board()
        position = BoardMapper.pixel_to_position(board, x, y)
        if position is None:
            return

        if self._selected_position is None:
            if not board.is_empty(position):
                self._selected_position = position
            return

        if (
            not board.is_empty(position)
            and RuleEngine.are_same_color(board, self._selected_position, position)
        ):
            self._selected_position = position
            return

        if game_engine.is_piece_moving(self._selected_position):
            self._selected_position = None
            return

        game_engine.try_move(self._selected_position, position)
        self._selected_position = None
