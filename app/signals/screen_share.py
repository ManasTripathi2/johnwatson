from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class ScreenShareSignal(Signal):
    """
    Produces evidence when a participant starts sharing
    their screen during the interview.
    """

    name = "screen_share"

    SCORE = 0.75

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.SCREEN_SHARE_STARTED:
            return None

        participant = context.get_participant(
            event.participant_id
        )

        if participant is None:
            return None

        participant.screen_sharing = True

        return Evidence(
            participant_id=participant.participant_id,
            signal=SignalType.SCREEN_SHARE,
            score=self.SCORE,
            reason="Participant started screen sharing.",
        )