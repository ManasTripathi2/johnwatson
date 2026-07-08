from dataclasses import dataclass, field

from app.models.interview import Interview
from app.models.participant import Participant


@dataclass
class InterviewContext:
    """
    Shared context available to every signal during processing.
    """

    interview: Interview

    participants: dict[str, Participant] = field(default_factory=dict)

    def get_participant(
        self,
        participant_id: str,
    ) -> Participant | None:
        return self.participants.get(participant_id)

    def add_participant(
        self,
        participant: Participant,
    ) -> None:
        self.participants[participant.participant_id] = participant