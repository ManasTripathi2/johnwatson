from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Participant:
    """
    Represents a participant in an interview meeting.

    The participant_id is the only stable identifier.
    Display names may change during the meeting.
    """

    participant_id: str
    display_name: str

    email: str | None = None

    joined_at: datetime | None = None
    left_at: datetime | None = None

    camera_on: bool = False
    microphone_on: bool = False
    screen_sharing: bool = False
    active: bool = True

    speaking_time: float = 0.0
    speaking_turns: int = 0

    confidence: float = 0.0

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def rename(self, name: str) -> None:
        self.display_name = name
        self.updated_at = datetime.utcnow()

    def join(self) -> None:
        self.active = True
        self.joined_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def leave(self) -> None:
        self.active = False
        self.left_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_speaking_time(self, duration: float) -> None:
        self.speaking_time += duration
        self.speaking_turns += 1
        self.updated_at = datetime.utcnow()

    def update_confidence(self, score: float) -> None:
        self.confidence = max(0.0, min(score, 1.0))
        self.updated_at = datetime.utcnow()