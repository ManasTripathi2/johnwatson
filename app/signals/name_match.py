from rapidfuzz import fuzz

from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.signals.base import Signal

from app.services.context import InterviewContext


class NameMatchSignal(Signal):
    """
    Generates evidence by comparing the participant's
    display name with the expected candidate name.
    """

    name = "name_match"

    def __init__(self, candidate_name: str):
        self.candidate_name = candidate_name

    def process(
    self,
    event: Event,
    context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.PARTICIPANT_JOINED:
            return None

        display_name = event.get("display_name")

        if not display_name:
            return None

        similarity = fuzz.token_sort_ratio(
            display_name,
            self.candidate_name
        )

        score = similarity / 100.0

        return Evidence(
            participant_id=event.participant_id,
            signal=SignalType.NAME_MATCH,
            score=score,
            reason=f"Name similarity = {similarity:.1f}%"
        )