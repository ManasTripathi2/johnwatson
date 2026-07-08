from app.events.event import Event
from app.fusion.bayesian import BayesianFusionEngine
from app.fusion.confidence import ConfidenceState
from app.signals.engine import SignalEngine


class InterviewEngine:
    """
    Coordinates the complete interview identification pipeline.
    """

    def __init__(
        self,
        signal_engine: SignalEngine,
        fusion_engine: BayesianFusionEngine,
    ) -> None:

        self.signal_engine = signal_engine
        self.fusion_engine = fusion_engine

        self._states: dict[str, ConfidenceState] = {}

    def process(self, event: Event) -> list[ConfidenceState]:

        evidence_list = self.signal_engine.process(event)

        for evidence in evidence_list:

            confidence = self.fusion_engine.update(evidence)

            state = self._states.get(evidence.participant_id)

            if state is None:
                state = ConfidenceState(
                    participant_id=evidence.participant_id
                )

                self._states[evidence.participant_id] = state

            state.update(
                confidence=confidence,
                evidence=evidence,
            )

        return self.rankings()

    def rankings(self) -> list[ConfidenceState]:

        return sorted(
            self._states.values(),
            key=lambda state: state.confidence,
            reverse=True,
        )

    def get_state(
        self,
        participant_id: str,
    ) -> ConfidenceState | None:

        return self._states.get(participant_id)

    def reset(self) -> None:

        self._states.clear()
        self.fusion_engine.reset()