# P4_Eventos/event_bus.py
"""
PARADIGMA 4: Declarativo
Patrón Publicador / Suscriptor (Observer) para desacoplar componentes.
"""

from typing import Callable, Dict, List, Any
from datetime import datetime


class Event:
    def __init__(self, name: str, data: Dict[str, Any]):
        self.name = name
        self.data = data
        self.timestamp = datetime.now()

    def __repr__(self) -> str:
        return f"<Event '{self.name}' at {self.timestamp.strftime('%H:%M:%S')}>"


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._history: List[Event] = []

    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> None:
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, data: Dict[str, Any]) -> None:
        event = Event(event_name, data)
        self._history.append(event)
        
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(event)

    def get_history(self) -> List[Event]:
        return list(self._history)


bus_global = EventBus()
