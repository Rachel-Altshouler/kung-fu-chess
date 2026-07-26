from __future__ import annotations

from bus.event_bus import EventBus
from bus.event_types import Events

#לעקוב אחרי הניקוד של כל שחקן
class ScoreBoard:
    """Keeps scores updated via SCORE_UPDATED events."""

    def __init__(self):
        self.white_score = 0
        self.black_score = 0

    def subscribe(self, bus: EventBus):
        bus.subscribe(Events.SCORE_UPDATED, self.on_score_updated)

    def on_score_updated(self, data):
        if not data:
            return
        self.white_score = data.get("white", self.white_score)
        self.black_score = data.get("black", self.black_score)
