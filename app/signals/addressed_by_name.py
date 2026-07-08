from rapidfuzz import fuzz

from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class AddressedByNameSignal(Signal):
    """
    Produces evidence when the candidate's name is mentioned
    in a transcript segment.
    """

    name = "addressed_by_name"

    MATCH_THRESHOLD = 80

    def __init__(self, candidate_name: str) -> None:
        self.candidate_name = candidate_name.lower()

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.TRANSCRIPT_RECEIVED:
            return None

        transcript = event.get("text", "").lower()

        if not transcript:
            return None

        similarity = fuzz.partial_ratio(
            self.candidate_name,
            transcript,
        )

        if similarity < self.MATCH_THRESHOLD:
            return None

        score = similarity / 100.0

        return Evidence(
            participant_id=event.participant_id,
            signal=SignalType.ADDRESSED_BY_NAME,
            score=score,
            reason=(
                f"Candidate name detected in transcript "
                f"({similarity:.1f}% similarity)."
            ),
        )