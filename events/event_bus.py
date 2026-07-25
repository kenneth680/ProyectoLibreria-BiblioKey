# events/event_bus.py
"""
Paradigma Orientado a Eventos (Event-Driven / Reactivo).
Patrón Publicador/Suscriptor (Observer) para desacoplar componentes.
Cualquier acción relevante publica un evento al cual reaccionan los suscriptores.
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
    """Bus Central de Eventos (Singleton / Instancia Compartida)."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._history: List[Event] = []

    def subscribe(self, event_name: str, callback: Callable[[Event], None]) -> None:
        """Registra una función oyente/reactiva para un tipo de evento."""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, data: Dict[str, Any]) -> None:
        """Dispara un evento y notifica sincrónicamente a todos sus suscriptores."""
        event = Event(event_name, data)
        self._history.append(event)
        
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                callback(event)

    def get_history(self) -> List[Event]:
        """Inmutabilidad opcional: retorna copia del historial de eventos."""
        return list(self._history)


# Instancia global por defecto del bus de eventos
bus_global = EventBus()
