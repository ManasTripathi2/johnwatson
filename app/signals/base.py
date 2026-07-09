from abc import ABC, abstractmethod

from app.evidence.evidence import Evidence
from app.events.event import Event
from app.services.context import InterviewContext


class Signal(ABC):
    """
    Base class for every signal in the system.
    """

    name: str

    @abstractmethod
    def process(
        self,
        event: Event,
        context: InterviewContext,
    ) -> Evidence | None:
        raise NotImplementedError

    def reset(self) -> None:
        return None
