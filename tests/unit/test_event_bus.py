import unittest

from engine.game_engine import GameEngine
from bus import Events, create_event_system
from bus.event_bus import EventBus
from domain.board import ChessBoard


class TestEventBus(unittest.TestCase):
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []

        bus.subscribe(Events.SCORE_UPDATED, lambda data: received.append(data))
        bus.publish(Events.SCORE_UPDATED, {"white": 3, "black": 0})

        self.assertEqual(received, [{"white": 3, "black": 0}])

    def test_score_and_move_log_subscribers(self):
        bus, score_board, move_log_panel, sound, animations = create_event_system(
            sound_enabled=False,
        )
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "bP"],
            [".", ".", "."],
            [".", ".", "."],
        ])
        engine = GameEngine(board, event_bus=bus)
        engine.notify_game_started()

        self.assertEqual(animations.mode, "start")
        self.assertEqual(sound.last_sound, "start")

        engine.handle_click(50, 50)
        engine.handle_click(250, 50)
        self.assertEqual(sound.last_sound, "move")

        engine.handle_wait(200)

        self.assertEqual(score_board.white_score, 1)
        self.assertEqual(len(move_log_panel.records), 1)
        self.assertEqual(move_log_panel.records[0].captured_token, "bP")
        self.assertEqual(sound.last_sound, "capture")

    def test_game_ended_event(self):
        bus, _scores, _moves, sound, animations = create_event_system(
            sound_enabled=False,
        )
        board = ChessBoard()
        board.set_grid([
            ["wR", ".", "bK"],
            [".", ".", "."],
            ["wK", ".", "."],
        ])
        engine = GameEngine(board, event_bus=bus)
        engine.try_move((0, 0), (0, 2))
        engine.handle_wait(200)

        self.assertTrue(engine.is_game_over())
        self.assertEqual(animations.mode, "end")
        self.assertEqual(sound.last_sound, "end")


if __name__ == "__main__":
    unittest.main()
