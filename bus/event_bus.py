from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

from bus.event_types import Events


Callback = Callable[[Any], None]

#זו המחלקה שמממשת את תבנית הפרסום
class EventBus:
    def __init__(self):
        self._subscribers: dict[Events, list[Callback]] = defaultdict(list)

    def subscribe(self, event_type: Events, callback: Callback):
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: Events, callback: Callback):
        callbacks = self._subscribers.get(event_type)
        if not callbacks:
            return
        if callback in callbacks:
            callbacks.remove(callback)

    #זו הפונקציה שמפעילה את כל המנגנון: עוברת על כל הפונקציות הרשומות לסוג האירוע הזה, וקוראת לכל אחת מהן עם ה-data.
    def publish(self, event_type: Events, data: Any = None):
        for callback in list(self._subscribers.get(event_type, [])):
            callback(data)
