from datetime import datetime

from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class JoinTimeSignal(Signal):
    """
    Produces evidence based on how close the participant
    joined to the scheduled interview start time.
    """

    name = "join_time"

    MAX_DELAY_SECONDS = 600

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.PARTICIPANT_JOINED:
            return None

        participant = context.get_participant(event.participant_id)

        if participant is None:
            return None

        joined_at = participant.joined_at or event.timestamp
        interview_start = context.interview.started_at

        delay = abs(
            (joined_at - interview_start).total_seconds()
        )

        score = max(
            0.0,
            1 - (delay / self.MAX_DELAY_SECONDS),
        )

        return Evidence(
            participant_id=participant.participant_id,
            signal=SignalType.JOIN_TIME,
            score=score,
            reason=(
                f"Joined {int(delay)} seconds from "
                f"scheduled interview start."
            ),
        )