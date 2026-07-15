class GameState:
    def __init__(self, board):
        self._board = board
        self._clock = 0
        self._active_movements = []
        self._next_movement_id = 1
        self._game_over = False

    def get_board(self):
        return self._board

    def get_clock(self) -> int:
        return self._clock

    def is_game_over(self) -> bool:
        return self._game_over

    def set_game_over(self):
        self._game_over = True

    def advance_clock(self, milliseconds: int):
        self._clock += milliseconds

    def get_active_movements(self):
        return list(self._active_movements)

    def get_active_movements_ref(self):
        return self._active_movements

    def allocate_movement_id(self) -> int:
        movement_id = self._next_movement_id
        self._next_movement_id += 1
        return movement_id

    def add_movement(self, movement):
        self._active_movements.append(movement)

    def remove_movement(self, movement):
        self._active_movements.remove(movement)
