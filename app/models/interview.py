from dataclasses import dataclass, field
from datetime import datetime

from app.models.participant import Participant


@dataclass
class Interview:
    """
    Represents a single interview session.
    """

    interview_id: str

    candidate_name: str
    candidate_email: str | None = None

    interviewer_names: list[str] = field(default_factory=list)

    participants: dict[str, Participant] = field(default_factory=dict)

    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None

    def add_participant(self, participant: Participant) -> None:
        self.participants[participant.participant_id] = participant

    def remove_participant(self, participant_id: str) -> None:
        participant = self.participants.get(participant_id)

        if participant:
            participant.leave()

    def get_participant(self, participant_id: str) -> Participant | None:
        return self.participants.get(participant_id)

    def active_participants(self) -> list[Participant]:
        return [
            participant
            for participant in self.participants.values()
            if participant.active
        ]

    def finish(self) -> None:
        self.ended_at = datetime.utcnow()