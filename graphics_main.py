import cv2

from engine.game_engine import GameEngine
from model.board import ChessBoard
from model.constants import GraphicsConstants
from view.renderer import Renderer
from view.time_format import player_name_hebrew


def main():
    board = ChessBoard.create_standard_setup()
    engine = GameEngine(board)
    renderer = Renderer()
    window_name = GraphicsConstants.WINDOW_NAME
    victory_announced = False

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    def on_mouse(event, x, y, flags, param):
        if engine.is_game_over():
            return
        if event not in (cv2.EVENT_LBUTTONDOWN, cv2.EVENT_RBUTTONDOWN):
            return

        position = Renderer.pixel_to_board_position(engine.get_board(), x, y)
        if position is None:
            return

        row, col = position
        pixel_x, pixel_y = Renderer.board_position_to_engine_pixels(row, col)

        if event == cv2.EVENT_LBUTTONDOWN:
            engine.handle_click(pixel_x, pixel_y)
        else:
            engine.handle_jump(pixel_x, pixel_y)

    cv2.setMouseCallback(window_name, on_mouse)

    while True:
        if not engine.is_game_over():
            engine.handle_wait(GraphicsConstants.FRAME_DELAY_MS)

        snapshot = engine.get_snapshot()
        canvas = renderer.render(snapshot)
        cv2.resizeWindow(window_name, canvas.img.shape[1], canvas.img.shape[0])

        if engine.is_game_over() and not victory_announced:
            if engine.is_stalemate():
                print("פט - תיקו")
            else:
                winner_name = player_name_hebrew(engine.get_winner())
                print(f"מט! מי ניצח: {winner_name}")
                print(f"ניצחון של {winner_name}")
            victory_announced = True

        key = canvas.show_loop(window_name, GraphicsConstants.FRAME_DELAY_MS)
        if key in (ord("q"), ord("Q"), 27):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
