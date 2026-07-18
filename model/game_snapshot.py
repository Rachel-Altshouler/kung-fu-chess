class GameSnapshot:
    def __init__(
        self,
        clock,
        white_score,
        black_score,
        pieces,
        rows,
        cols,
        selected_position=None,
        game_over=False,
        winner=None,
        is_stalemate=False,
    ):
        self.clock = clock
        self.white_score = white_score
        self.black_score = black_score
        self.pieces = pieces
        self.rows = rows
        self.cols = cols
        self.selected_position = selected_position
        self.game_over = game_over
        self.winner = winner
        self.is_stalemate = is_stalemate
