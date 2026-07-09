from rapidfuzz import fuzz

from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class AddressedByNameSignal(Signal):
    """
    Produces evidence when the candidate appears to be addressed.

    Transcript events identify the speaker, not the addressee. This signal
    stores a name mention and credits the next participant who speaks.
    """

    name = "addressed_by_name"

    MATCH_THRESHOLD = 80
    MAX_SCORE = 0.65

    def __init__(self, candidate_name: str) -> None:
        self.candidate_name = candidate_name.lower()
        self._pending_score: float | None = None
        self._pending_reason: str | None = None

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type == EventType.TRANSCRIPT_RECEIVED:
            self._capture_name_mention(event)
            return None

        if event.event_type == EventType.SPEECH_STARTED:
            return self._consume_pending(event, context)

        return None

    def _capture_name_mention(self, event: Event) -> None:
        transcript = event.get("text", "").lower()

        if not transcript:
            return None

        similarity = fuzz.partial_ratio(self.candidate_name, transcript)

        if similarity >= self.MATCH_THRESHOLD:
            scaled = (
                (similarity - self.MATCH_THRESHOLD)
                / (100 - self.MATCH_THRESHOLD)
            )
            self._pending_score = scaled * self.MAX_SCORE
            self._pending_reason = (
                f"Candidate name detected in transcript "
                f"({similarity:.1f}% similarity)."
            )

        return None

    def _consume_pending(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:
        if self._pending_score is None:
            return None

        participant = context.get_participant(event.participant_id)

        if participant is None:
            return None

        score = self._pending_score
        reason = self._pending_reason or ""
        self._pending_score = None
        self._pending_reason = None

        return Evidence(
            participant_id=participant.participant_id,
            signal=SignalType.ADDRESSED_BY_NAME,
            score=score,
            reason=reason,
        )

    def reset(self) -> None:
        self._pending_score = None
        self._pending_reason = None
