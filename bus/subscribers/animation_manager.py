from __future__ import annotations
from domain.constants import subscribers
from bus.event_bus import EventBus
from bus.event_types import Events
from rendering.time_format import player_name_english


class AnimationManager:
    """Handles short start/end overlay animations driven by game events."""



    def __init__(self):
        self.mode = None
        self.message = ""
        self.frames_left = 0

    def subscribe(self, bus: EventBus):
        bus.subscribe(Events.GAME_STARTED, self.on_game_started)
        bus.subscribe(Events.GAME_ENDED, self.on_game_ended)

    def on_game_started(self, data):
        self.mode = "start"
        self.message = "Game Start!"
        self.frames_left = subscribers.START_FRAMES

    def on_game_ended(self, data):
        data = data or {}
        self.mode = "end"
        if data.get("is_stalemate"):
            self.message = "Stalemate - Draw"
        else:
            winner = player_name_english(data.get("winner"))
            self.message = f"{winner} wins!"
        self.frames_left = subscribers.END_FRAMES

    def tick(self):
        if self.frames_left <= 0:
            if self.mode == "start":
                self.mode = None
                self.message = ""
            return
        self.frames_left -= 1
        if self.frames_left <= 0 and self.mode == "start":
            self.mode = None
            self.message = ""

    @property
    def is_active(self) -> bool:
        return self.mode is not None and bool(self.message)
