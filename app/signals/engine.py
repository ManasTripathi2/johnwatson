from app.evidence.evidence import Evidence
from app.events.event import Event
from app.signals.base import Signal


class SignalEngine:
    """
    Runs all registered signals for an incoming event.
    """

    def __init__(self) -> None:
        self._signals: list[Signal] = []

    def register(self, signal: Signal) -> None:
        """
        Register a signal with the engine.
        """
        self._signals.append(signal)

    def process(self, event: Event) -> list[Evidence]:
        """
        Process an event through every registered signal.

        Returns only the evidence objects that were produced.
        """

        evidence = []

        for signal in self._signals:
            result = signal.process(event)

            if result is not None:
                evidence.append(result)

        return evidence

    @property
    def signals(self) -> list[Signal]:
        return self._signals