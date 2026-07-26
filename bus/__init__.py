from bus.event_bus import EventBus
from bus.event_types import Events
from bus.subscribers import (
    AnimationManager,
    MoveLogPanel,
    ScoreBoard,
    SoundManager,
)


def create_event_system(sound_enabled: bool = True):
    bus = EventBus()
    score_board = ScoreBoard()
    move_log_panel = MoveLogPanel()
    sound_manager = SoundManager(enabled=sound_enabled)
    animation_manager = AnimationManager()

    score_board.subscribe(bus)
    move_log_panel.subscribe(bus)
    sound_manager.subscribe(bus)
    animation_manager.subscribe(bus)

    return bus, score_board, move_log_panel, sound_manager, animation_manager


__all__ = [
    "EventBus",
    "Events",
    "AnimationManager",
    "MoveLogPanel",
    "ScoreBoard",
    "SoundManager",
    "create_event_system",
]
