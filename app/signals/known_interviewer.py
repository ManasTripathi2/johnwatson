from rapidfuzz import fuzz

from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class KnownInterviewerSignal(Signal):
    """
    Produces negative evidence for participants whose
    display name matches a known interviewer.
    """

    name = "known_interviewer"

    MATCH_THRESHOLD = 90

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.PARTICIPANT_JOINED:
            return None

        participant = context.get_participant(
            event.participant_id
        )

        if participant is None:
            return None

        display_name = participant.display_name.lower()

        for interviewer in context.interview.interviewer_names:

            similarity = fuzz.token_sort_ratio(
                display_name,
                interviewer.lower(),
            )

            if similarity >= self.MATCH_THRESHOLD:

                return Evidence(
                    participant_id=participant.participant_id,
                    signal=SignalType.KNOWN_INTERVIEWER,
                    score=-0.80,
                    reason=(
                        f"Participant matches known interviewer "
                        f"'{interviewer}'."
                    ),
                )

        return None
