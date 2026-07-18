"""Static one-frame board preview using Renderer + GameSnapshot."""
from engine.game_engine import GameEngine
from model.board import ChessBoard
from view.renderer import Renderer


def main():
    board = ChessBoard.create_standard_setup()
    engine = GameEngine(board)
    renderer = Renderer()
    snapshot = engine.get_snapshot()
    canvas = renderer.render(snapshot)
    canvas.show()


if __name__ == "__main__":
    main()
