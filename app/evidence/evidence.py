from dataclasses import dataclass, field
from datetime import datetime

from app.core.enums import EvidenceSource, SignalType


@dataclass(slots=True)
class Evidence:
    """
    A single piece of evidence produced by a signal module.

    The fusion engine combines multiple evidence objects
    to estimate the probability that a participant is
    the interview candidate.
    """

    participant_id: str

    signal: SignalType

    score: float

    source: EvidenceSource = EvidenceSource.RULE

    reason: str = ""

    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not -1.0 <= self.score <= 1.0:
            raise ValueError("Evidence score must be between -1 and 1.")