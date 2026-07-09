import json
import time
from collections.abc import Iterator
from datetime import timedelta
from pathlib import Path

from app.core.enums import EventType
from app.events.event import Event
from app.fusion.confidence import ConfidenceState
from app.services.interview_engine import InterviewEngine


class ReplayEngine:
    """
    Replays recorded interview events.

    Events are executed according to their recorded offsets
    and passed through the InterviewEngine.
    """

    def __init__(
        self,
        interview_engine: InterviewEngine,
    ) -> None:

        self.interview_engine = interview_engine

    def load(
        self,
        path: str | Path,
    ) -> list[dict]:

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def replay(
        self,
        path: str | Path,
    ) -> None:

        for event, states in self.iter_replay(path, sleep=True):

            print("=" * 60)
            print(f"EVENT : {event.event_type.value}")
            print(f"PARTICIPANT : {event.participant_id}")

            for state in states:
                print(
                    f"{state.participant_id:<10}"
                    f"{state.confidence:.3f}"
                )

    def iter_replay(
        self,
        path: str | Path,
        sleep: bool = False,
    ) -> Iterator[tuple[Event, list[ConfidenceState]]]:
        events = self.load(path)
        previous_offset = 0.0

        for item in events:

            offset = item["offset_seconds"]
            delay = offset - previous_offset

            if sleep and delay > 0:
                time.sleep(delay)

            event = self._build_event(item)
            states = self.interview_engine.process(event)

            yield event, states

            previous_offset = offset

    def _build_event(
        self,
        item: dict,
    ) -> Event:
        offset = item["offset_seconds"]
        timestamp = (
            self.interview_engine.interview.started_at
            + timedelta(seconds=offset)
        )

        event = Event(
            event_type=EventType(item["event_type"]),
            participant_id=item["participant_id"],
            timestamp=timestamp,
        )

        for key, value in item.get("data", {}).items():
            event.add(key, value)

        return event
