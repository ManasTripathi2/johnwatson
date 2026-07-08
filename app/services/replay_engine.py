import json
import time
from pathlib import Path

from app.core.enums import EventType
from app.events.event import Event
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

        events = self.load(path)

        previous_offset = 0.0

        for item in events:

            offset = item["offset_seconds"]

            delay = offset - previous_offset

            if delay > 0:
                time.sleep(delay)

            event = Event(
                event_type=EventType(item["event_type"]),
                participant_id=item["participant_id"],
            )

            for key, value in item.get("data", {}).items():
                event.add(key, value)

            states = self.interview_engine.process(event)

            print("=" * 60)
            print(f"EVENT : {event.event_type.value}")
            print(f"PARTICIPANT : {event.participant_id}")

            for state in states:
                print(
                    f"{state.participant_id:<10}"
                    f"{state.confidence:.3f}"
                )

            previous_offset = offset