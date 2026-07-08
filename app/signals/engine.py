from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext
from app.signals.base import Signal


class SignalEngine:

    def __init__(self) -> None:
        self._signals: list[Signal] = []

    def register(
        self,
        signal: Signal,
    ) -> None:
        self._signals.append(signal)

    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> list[Evidence]:

        evidence = []

        for signal in self._signals:

            result = signal.process(
                event,
                context,
            )

            if result is not None:
                evidence.append(result)

        return evidence

    @property
    def signals(self) -> list[Signal]:
        return self._signals