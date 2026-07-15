from game_io.board_printer import BoardPrinter


class Renderer:
    @staticmethod
    def render_text(board) -> str:
        return BoardPrinter.get_canonical_representation(board)
