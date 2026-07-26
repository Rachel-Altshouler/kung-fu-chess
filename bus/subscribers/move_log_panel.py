from __future__ import annotations

from bus.event_bus import EventBus
from bus.event_types import Events

#מחלקה המנהלת את היסטוריית המהלכים של המשחק
class MoveLogPanel:
    """Keeps move history updated via MOVE_LOGGED events."""
    #רשימה ריקה שתאגור את כל רשומות המהלכים שבוצעו במשחק, לפי הסדר.
    def __init__(self):
        self.records = []

    #הרשמה לאירוע
    def subscribe(self, bus: EventBus):
        bus.subscribe(Events.MOVE_LOGGED, self.on_move_logged)

    #פונקציה שמטפלת באירוע
    def on_move_logged(self, data):
        if not data:
            return
        record = data.get("record")
        if record is not None:
            self.records.append(record)
    #פונקציה שמחזירה מלכים לפי צבע
    def get_for_color(self, color: str):
        return [record for record in self.records if record.color == color]
