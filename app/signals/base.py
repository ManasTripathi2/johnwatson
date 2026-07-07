from abc import ABC, abstractmethod

from app.events.event import Event
from app.evidence.evidence import Evidence


class Signal(ABC):
    """
    Base class for every signal in the system.

    Each signal observes an event and may produce
    evidence for or against a participant being
    the interview candidate.
    """

    name: str

    @abstractmethod
    def process(self, event: Event) -> Evidence | None:
        """
        Process an event.

        Returns:
            Evidence if the signal has something meaningful
            to contribute, otherwise None.
        """
        raise NotImplementedError