from app.core.enums import EventType, SignalType
from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class SpeakingPatternSignal(Signal):
    """
    Produces evidence from participant speaking behaviour.

    The signal observes speech events and continuously updates
    the participant's speaking statistics.
    """

    name = "speaking_pattern"

    MAX_EXPECTED_SPEAKING_TIME = 300.0
    MAX_SCORE = 0.35

    def __init__(self) -> None:
        self._last_scores: dict[str, float] = {}

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:

        if event.event_type != EventType.SPEECH_ENDED:
            return None

        participant = context.get_participant(event.participant_id)

        if participant is None:
            return None

        duration = float(event.get("duration", 0.0))

        if duration <= 0:
            return None

        previous_score = self._last_scores.get(
            participant.participant_id,
            0.0,
        )

        participant.add_speaking_time(duration)

        normalized_time = min(
            participant.speaking_time / self.MAX_EXPECTED_SPEAKING_TIME,
            1.0,
        )

        turn_bonus = min(
            participant.speaking_turns / 20.0,
            1.0,
        )

        cumulative_score = (
            (normalized_time * 0.8) + (turn_bonus * 0.2)
        ) * self.MAX_SCORE

        score = max(0.0, cumulative_score - previous_score)
        self._last_scores[participant.participant_id] = cumulative_score

        if score <= 1e-6:
            return None

        return Evidence(
            participant_id=participant.participant_id,
            signal=SignalType.SPEAKING_PATTERN,
            score=score,
            reason=(
                f"Speaking time "
                f"{participant.speaking_time:.1f}s "
                f"across {participant.speaking_turns} turns."
            ),
        )

    def reset(self) -> None:
        self._last_scores.clear()
