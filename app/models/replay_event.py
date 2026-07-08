from dataclasses import dataclass
from datetime import datetime

from app.events.event import Event


@dataclass
class ReplayEvent:
    """
    Represents an event scheduled for replay.
    """

    offset_seconds: float
    event: Event

    def scheduled_time(
        self,
        start_time: datetime,
    ) -> datetime:
        from datetime import timedelta

        return start_time + timedelta(
            seconds=self.offset_seconds
        )