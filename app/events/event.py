from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.enums import EventType


@dataclass
class Event:
    """
    Represents a single event generated during an interview.

    Every update flowing through the system is represented as an Event.
    """

    event_type: EventType

    participant_id: str

    timestamp: datetime = field(default_factory=datetime.utcnow)

    data: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def add(self, key: str, value: Any) -> None:
        self.data[key] = value

    def __getitem__(self, key: str) -> Any:
        return self.data[key]