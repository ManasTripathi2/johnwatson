from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class SpeakingPatternSignal(Signal):
    """
    Produces evidence based on participant speaking behaviour.

    The assumption is simple:
    candidates usually spend more time answering questions,
    therefore they accumulate more speaking time than observers.
    """

    name = "speaking_pattern"

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.SPEECH_ENDED:
            return None

        participant = context.get_participant(
            event.participant_id
        )

        if participant is None:
            return None

        duration = event.get("duration", 0.0)

        participant.add_speaking_time(duration)

        score = min(
            participant.speaking_time / 300.0,
            1.0,
        )

        return Evidence(
            participant_id=participant.participant_id,
            signal=SignalType.SPEAKING_PATTERN,
            score=score,
            reason=(
                f"Participant has spoken "
                f"{participant.speaking_time:.1f} seconds."
            ),
        )